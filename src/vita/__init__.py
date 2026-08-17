import typer

def main() -> None:
    typer.echo("Bienvenido a tu asistente V.I.T.A. ¿En qué puedo ayudarte hoy?")

    while True:
        try: 
            message = typer.prompt("V.I.T.A.")
        except (KeyboardInterrupt, EOFError):
            typer.echo("\nHasta luego.")
            break

        if message.lower() in ("exit", "quit"):
            typer.echo("Hasta luego.")
            break

        if not message.strip():
            continue

        typer.echo(f"Has dicho: {message}")

if __name__ == "__main__":
    typer.run(main)
