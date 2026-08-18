import typer
from vita.llm.ollama import OllamaClient

def main() -> None:
    client = OllamaClient()
    typer.echo("Bienvenido a tu asistente V.I.T.A. ¿En qué puedo ayudarte hoy?")

    while True:
        try: 
            message = typer.prompt("V.I.T.A.")
        except (KeyboardInterrupt, EOFError):
            typer.echo("\nHasta luego.")
            break

        if message.lower() in ("salir", "adios", "quit", "exit"):
            typer.echo("Hasta luego.")
            break

        if not message.strip():
            continue

        response = client.chat(message)
        typer.echo(f"\n{response}\n")

if __name__ == "__main__":
    typer.run(main)
