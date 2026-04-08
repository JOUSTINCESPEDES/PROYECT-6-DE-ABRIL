import os
import pandas as pd
from flask import Flask, render_template, request, redirect, session, jsonify
from database import (conectar, obtenerusuarios, insertar_masivo,
                      buscar_estudiantes, editar_estudiante, eliminar_estudiante,
                      obtener_estudiantes_por_carrera)
from dashprincipal import creartablero


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_local_dev")

creartablero(app)


# ── HEADERS ANTI-CACHÉ ───────────────────────────────────────────────────────
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"]        = "no-cache"
    response.headers["Expires"]       = "0"
    return response


# ── LOGIN ────────────────────────────────────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("usuario",    "").strip()
        password = request.form.get("contraseña", "").strip()

        if not username or not password:
            error = "Por favor ingresa usuario y contraseña."
            return render_template("login.html", error=error)

        usuario = obtenerusuarios(username)

        if usuario and isinstance(usuario, dict):
            contrasena_bd = usuario.get("contraseña")
            rol           = usuario.get("rol", "estudiante").lower()

            if contrasena_bd and contrasena_bd == password:
                session["username"]       = usuario.get("nombre_usuario") or username
                session["rol"]            = rol
                session["nombre_completo"]= usuario.get("nombre_usuario", username)

                if rol == "admin":
                    return redirect("/dashprincipal")
                elif rol == "profesor":
                    return redirect("/profesor")
                elif rol == "estudiante":
                    return redirect("/estudiante")
                else:
                    error = "Rol no reconocido. Contacta al administrador."
            else:
                error = "Usuario o contraseña incorrectos."
        else:
            error = "Usuario o contraseña incorrectos."

    return render_template("login.html", error=error)


# ── HELPER: redirige según rol ───────────────────────────────────────────────
def redirect_seguro_por_rol():
    rol = session.get("rol")
    if rol == "admin":      return redirect("/dashprincipal")
    elif rol == "profesor": return redirect("/profesor")
    elif rol == "estudiante": return redirect("/estudiante")
    else:
        session.clear()
        return redirect("/")

# ── ADMIN ────────────────────────────────────────────────────────────────────
@app.route("/dashprincipal")
def dashprincipal():
    if "username" not in session:      return redirect("/")
    if session.get("rol") != "admin":  return redirect_seguro_por_rol()
    return render_template("dashprinci.html", usuario=session["username"])


# ── PROFESOR ─────────────────────────────────────────────────────────────────
@app.route("/profesor")
def profesor_dashboard():
    if "username" not in session:        return redirect("/")
    if session.get("rol") != "profesor": return redirect_seguro_por_rol()

    usuario = obtenerusuarios(session["username"])
    if not usuario:
        session.clear()
        return redirect("/")

    carrera_profesor = usuario.get("carrera")
    if not carrera_profesor:
        return "El profesor no tiene asignada ninguna carrera.", 400

    estudiantes_carrera = obtener_estudiantes_por_carrera(carrera_profesor)

    return render_template(
        "profesor.html",
        usuario=session["username"],
        carrera=carrera_profesor,
        estudiantes=estudiantes_carrera
    )


# ── ESTUDIANTE ───────────────────────────────────────────────────────────────
@app.route("/estudiante")
def estudiante_dashboard():
    if "username" not in session:          return redirect("/")
    if session.get("rol") != "estudiante": return redirect_seguro_por_rol()

    usuario = obtenerusuarios(session["username"])
    if not usuario:
        session.clear()
        return redirect("/")

    from database import obtener_historial, obtener_stats_carrera, obtener_posicion_carrera

    id_estudiante = usuario.get("id_estudiante")
    carrera       = usuario.get("carrera_estudiante") or usuario.get("carrera")
    promedio      = float(usuario.get("promedio") or 0)

    historial = obtener_historial(id_estudiante) if id_estudiante else []
    stats     = obtener_stats_carrera(carrera)   if carrera       else {}
    posicion  = obtener_posicion_carrera(id_estudiante, carrera) if id_estudiante and carrera else None

    promedio_carrera = float(stats.get("promedio_carrera") or 0) if stats else 0
    diferencia       = round(promedio - promedio_carrera, 2)

    return render_template(
        "student_dashboard.html",
        usuario=session["username"],
        estudiante={
            "nombre":   usuario.get("nombre_estudiante") or session["username"],
            "edad":     usuario.get("edad"),
            "carrera":  carrera,
            "nota1":    float(usuario.get("nota1") or 0),
            "nota2":    float(usuario.get("nota2") or 0),
            "nota3":    float(usuario.get("nota3") or 0),
            "promedio": promedio,
        },
        historial=historial,
        stats=stats,
        posicion=posicion,
        diferencia=diferencia,
    )

#pdf
@app.route("/estudiante/reporte_pdf")
def descargar_reporte():
    if "username" not in session:          return redirect("/")
    if session.get("rol") != "estudiante": return redirect_seguro_por_rol()

    from database import obtener_historial, obtener_stats_carrera, obtener_posicion_carrera
    from reporte_pdf import generar_pdf
    from flask import send_file

    usuario       = obtenerusuarios(session["username"])
    id_estudiante = usuario.get("id_estudiante")
    carrera       = usuario.get("carrera_estudiante") or usuario.get("carrera")
    promedio      = float(usuario.get("promedio") or 0)

    historial        = obtener_historial(id_estudiante) if id_estudiante else []
    stats            = obtener_stats_carrera(carrera)   if carrera       else {}
    posicion         = obtener_posicion_carrera(id_estudiante, carrera) if id_estudiante and carrera else None
    promedio_carrera = float((stats or {}).get("promedio_carrera") or 0)
    diferencia       = round(promedio - promedio_carrera, 2)

    estudiante = {
        "nombre":   usuario.get("nombre_estudiante") or session["username"],
        "carrera":  carrera,
        "nota1":    float(usuario.get("nota1") or 0),
        "nota2":    float(usuario.get("nota2") or 0),
        "nota3":    float(usuario.get("nota3") or 0),
        "promedio": promedio,
    }

    pdf = generar_pdf(estudiante, historial, stats, posicion, diferencia)
    nombre_archivo = f"reporte_{estudiante['nombre'].replace(' ','_')}.pdf"

    return send_file(pdf, mimetype="application/pdf",
                     as_attachment=True, download_name=nombre_archivo)

# ── TOP ESTUDIANTES ──────────────────────────────────────────────────────────
@app.route("/top_estudiantes")
def top_estudiantes():
    if "username" not in session: return redirect("/")
    return render_template("top_estudiantes.html")

@app.route("/api/estudiantes/top")
def api_top():
    if "username" not in session:
        return jsonify({"ok": False, "error": "No autenticado"}), 401
    try:
        from database import obtener_top_estudiantes
        estudiantes = obtener_top_estudiantes(10)
        for e in estudiantes:
            e['promedio'] = float(e['promedio'])
        return jsonify({"ok": True, "estudiantes": estudiantes})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


# ── EDITAR ESTUDIANTE ────────────────────────────────────────────────────────
@app.route("/editar_estudiante")
def editar_estudiante_page():
    if "username" not in session: return redirect("/")
    return render_template("editar_estudiante.html")

@app.route("/api/estudiantes/buscar")
def api_buscar():
    if "username" not in session:
        return jsonify({"ok": False, "error": "No autenticado"}), 401
    nombre = request.args.get("nombre", "")
    try:
        estudiantes = buscar_estudiantes(nombre)
        return jsonify({"ok": True, "estudiantes": estudiantes})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "estudiantes": []})

@app.route("/api/estudiantes/editar", methods=["POST"])
def api_editar():
    if "username" not in session:
        return jsonify({"ok": False, "error": "No autenticado"}), 401
    datos = request.get_json()
    try:
        editar_estudiante(datos)
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Error al actualizar: {str(e)}"})

@app.route("/api/estudiantes/eliminar", methods=["POST"])
def api_eliminar():
    if "username" not in session:
        return jsonify({"ok": False, "error": "No autenticado"}), 401
    datos = request.get_json()
    try:
        eliminar_estudiante(datos["id_estudiante"])
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Error al eliminar: {str(e)}"})


# ── CARGA MASIVA ─────────────────────────────────────────────────────────────
@app.route("/carga_masiva", methods=["GET", "POST"])
def carga_masiva():
    if "username" not in session: return redirect("/")

    if request.method == "GET":
        return render_template("carga_masiva.html")

    if "archivo" not in request.files:
        return jsonify({"ok": False, "error": "No se recibió ningún archivo."})

    archivo = request.files["archivo"]

    if archivo.filename == "":
        return jsonify({"ok": False, "error": "No seleccionaste ningún archivo."})

    if not archivo.filename.endswith(('.xlsx', '.xls')):
        return jsonify({"ok": False, "error": "El archivo debe ser .xlsx o .xls"})

    try:
        df        = pd.read_excel(archivo)
        resultado = insertar_masivo(df)
        return jsonify({
            "ok":         True,
            "insertados": int(resultado["insertados"]),
            "duplicados": int(resultado["duplicados"]),
            "vacios":     int(resultado["vacios"]),
            "invalidos":  int(resultado["invalidos"]),
            "detalles":   resultado["errores"]
        })
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e), "detalles": []})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Error procesando el archivo: {str(e)}", "detalles": []})


# ── JUEGO ────────────────────────────────────────────────────────────────────
@app.route("/juego")
def juego():
    return render_template("gallina-pro.html")


# ── LOGOUT ───────────────────────────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)