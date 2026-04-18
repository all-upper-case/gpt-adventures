#!/usr/bin/env python3

from flask import Flask, redirect, render_template_string, request, url_for

from advent import new_game, run_command

app = Flask(__name__)

GAME_STATE = {'game': None, 'history': []}

PAGE_TEMPLATE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>GPT Adventures</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; background: #10131a; color: #f2f2f2; }
    .wrap { max-width: 900px; margin: 0 auto; padding: 20px; }
    .panel { background: #1a2030; border-radius: 12px; padding: 16px; margin-bottom: 16px; }
    .log { white-space: pre-wrap; line-height: 1.4; min-height: 300px; max-height: 420px; overflow-y: auto; }
    input[type=text] { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #3a4255; background: #0f1422; color: #fff; }
    button { padding: 10px 14px; border: none; border-radius: 8px; margin-right: 8px; cursor: pointer; }
    .row { margin-top: 12px; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>GPT Adventure Game</h1>
    <div class="panel">
      <div><strong>{{ title }}</strong></div>
      <div>{{ plot }}</div>
    </div>
    <div class="panel log">{{ history_text }}</div>
    <form method="post" action="{{ url_for('command') }}" class="panel">
      <label>What do you want to do?</label>
      <input type="text" name="command" autofocus placeholder="look, go north, take map, inventory">
      <div class="row">
        <button type="submit">Send command</button>
        <a href="{{ url_for('reset') }}"><button type="button">Reset game</button></a>
      </div>
    </form>
  </div>
</body>
</html>
"""


def _start_game():
    game = new_game()
    GAME_STATE['game'] = game
    GAME_STATE['history'] = [
        game['_title'],
        "",
        game['_plot'],
        "",
    ]
    return game


@app.get("/")
def home():
    game = GAME_STATE['game'] or _start_game()
    return render_template_string(
        PAGE_TEMPLATE,
        title=game.get('_title', 'Adventure'),
        plot=game.get('_plot', ''),
        history_text="\n".join(GAME_STATE['history']),
    )


@app.post("/command")
def command():
    game = GAME_STATE['game'] or _start_game()
    user_command = request.form.get("command", "").strip()
    if not user_command:
        return redirect(url_for('home'))

    GAME_STATE['history'].append(f"> {user_command}")
    game, output = run_command(game, user_command)
    GAME_STATE['game'] = game
    if output:
        GAME_STATE['history'].append(output)
    GAME_STATE['history'].append("")
    return redirect(url_for('home'))


@app.get("/reset")
def reset():
    _start_game()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=False)
