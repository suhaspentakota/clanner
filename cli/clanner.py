import typer, requests, os
from rich import print

app = typer.Typer()
API_URL = os.environ.get("CLANNER_API_URL", "http://localhost:8000/v1/chat")

@app.command()
def chat(prompt: str, retrieval: bool = typer.Option(False, help="Use local vector retrieval"), search: bool = typer.Option(False, help="Use Bing web search"), mode: str = typer.Option("mix_ai", help="Provider mode")):
    payload={"messages":[{"role":"user","content":prompt}],"mode":mode,"search":search,"retrieval":retrieval}
    resp=requests.post(API_URL,json=payload,timeout=120); resp.raise_for_status()
    data=resp.json()
    print("[bold green]Clanner:[/bold green]", data["output"])
    if data.get("citations"):
        print("\n[bold yellow]Citations:[/bold yellow]")
        for c in data["citations"]:
            print(f"- {c['title']}: {c['url']}")
    if data.get("provider_traces"):
        print("\n[bold cyan]Providers:[/bold cyan]")
        for p in data["provider_traces"]:
            print(f"- {p['provider']} ({p['model']}), {p['latency_ms']} ms")

if __name__ == "__main__":
    app()
