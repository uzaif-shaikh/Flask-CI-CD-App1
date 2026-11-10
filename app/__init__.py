from flask import Flask, jsonify, render_template, request, abort


def create_app():
    app = Flask(__name__)
    app.config["TODOS"] = []
    app.config["NEXT_ID"] = 1

    @app.route("/")
    def index():
        return render_template("index.html", todos=app.config["TODOS"])

    @app.route("/health")
    def health():
        # Used by Docker HEALTHCHECK and the Jenkins smoke test
        return jsonify(status="ok"), 200

    @app.route("/api/todos", methods=["GET"])
    def list_todos():
        return jsonify(app.config["TODOS"])

    @app.route("/api/todos", methods=["POST"])
    def add_todo():
        data = request.get_json(silent=True) or {}
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify(error="title is required"), 400
        todo = {"id": app.config["NEXT_ID"], "title": title, "done": False}
        app.config["NEXT_ID"] += 1
        app.config["TODOS"].append(todo)
        return jsonify(todo), 201

    @app.route("/api/todos/<int:todo_id>/toggle", methods=["POST"])
    def toggle_todo(todo_id):
        for todo in app.config["TODOS"]:
            if todo["id"] == todo_id:
                todo["done"] = not todo["done"]
                return jsonify(todo)
        abort(404)

    @app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
    def delete_todo(todo_id):
        before = len(app.config["TODOS"])
        app.config["TODOS"][:] = [t for t in app.config["TODOS"] if t["id"] != todo_id]
        if len(app.config["TODOS"]) == before:
            abort(404)
        return "", 204

    return app
