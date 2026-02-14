import os
import sys
import subprocess
import time
import requests
import json
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.align import Align
from rich.prompt import Prompt

console = Console()
ntfy_topic = None
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def print_banner():
    banner = """
  ▄▄▄▄▄                                                         
 ██▀▀▀▀█▄       █▄       █▄                                     
 ▀██▄  ▄▀       ██       ██       ▄              ▀▀ ▄           
   ▀██▄▄  ██ ██ ████▄ ▄████ ▄███▄ ███▄███▄ ▄▀▀█▄ ██ ████▄ ▄██▀█ 
 ▄   ▀██▄ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██ ▄█▀██ ██ ██ ██ ▀███▄ 
 ▀██████▀▄▀██▀█▄████▀▄█▀███▄▀███▀▄██ ██ ▀█▄▀█▄██▄██▄██ ▀██▄▄██▀ 
                                                
  ▄▄▄▄▄▄▄                                                       
 █▀██▀▀▀                                        █▄              
   ██     ▄           ▄              ▄         ▄██▄      ▄      
   ████   ████▄ ██ ██ ███▄███▄ ▄█▀█▄ ████▄▄▀▀█▄ ██ ▄███▄ ████▄  
   ██     ██ ██ ██ ██ ██ ██ ██ ██▄█▀ ██   ▄█▀██ ██ ██ ██ ██     
   ▀█████▄██ ▀█▄▀██▀█▄██ ██ ▀█▄▀█▄▄▄▄█▀  ▄▀█▄██▄██▄▀███▀▄█▀     
"""
    console.print(Panel(Align.center(banner), border_style="bold cyan"))


def send_notification(message):
    global ntfy_topic
    if ntfy_topic:
        try:
            requests.post(f"https://ntfy.sh/{ntfy_topic}", data=message.encode("utf-8"))
        except:
            console.print(
                Panel("[red]FAILED TO SEND NTFY NOTIFICATION[/red]", border_style="red")
            )


def run_command_with_spinner(command, description, output_file):
    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn(f"[bold cyan]{description.upper()}..."),
        transient=True,
        console=console,
    ) as progress:
        task = progress.add_task(description.upper(), start=False)
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        progress.start_task(task)
        while process.poll() is None:
            time.sleep(0.1)
        process.wait()

    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = set(line.strip() for line in f if line.strip())
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(lines)))
        return lines
    else:
        console.print(
            Panel(
                f"[red]{description.upper()} FAILED OR OUTPUT FILE MISSING.[/red]",
                border_style="red",
            )
        )
        return set()


CONFIG_FILE = os.path.join(BASE_DIR, "config.json")


def ask_ntfy_topic():
    global ntfy_topic

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                ntfy_topic = config.get("ntfy_topic")
                if ntfy_topic:
                    console.print(
                        Panel(
                            f"[green]LOADED NTFY TOPIC FROM CONFIG: [cyan]{ntfy_topic}[/cyan][/green]",
                            border_style="green",
                        )
                    )
                    return
        except Exception:
            console.print(
                Panel(
                    "[red]ERROR READING CONFIG FILE. ASKING MANUALLY...[/red]",
                    border_style="red",
                )
            )

    ntfy_topic = Prompt.ask(
        "[bold cyan]ENTER NTFY.SH TOPIC NAME (OR PRESS ENTER TO SKIP)[/bold cyan]"
    ).strip()

    if ntfy_topic:
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump({"ntfy_topic": ntfy_topic}, f)
            console.print(
                Panel(
                    f"[green]TOPIC SAVED TO [bold]config.json[/bold] FOR FUTURE USE.[/green]",
                    border_style="green",
                )
            )
        except Exception as e:
            console.print(f"[red]FAILED TO SAVE CONFIG: {e}[/red]")
    else:
        ntfy_topic = None
        console.print(
            Panel(
                "[yellow]NO NOTIFICATIONS WILL BE SENT.[/yellow]", border_style="yellow"
            )
        )


def main():
    print_banner()
    ask_ntfy_topic()

    website_name = Prompt.ask(
        "[bold cyan] PLEASE ENTER THE NAME OF THE FOLDER [/bold cyan]"
    ).strip()

    BASE_OUTPUT_DIR = r"W:\BugBounty"
    path = os.path.join(BASE_OUTPUT_DIR, website_name)
    os.makedirs(path, exist_ok=True)

    console.print(
        Panel(
            "[bold yellow] ENTER DOMAIN(S). SUBMIT EMPTY LINE TO FINISH.[/bold yellow]",
            border_style="yellow",
        )
    )
    domains = []
    while True:
        domain = Prompt.ask("[bold cyan]ENTER DOMAIN[/bold cyan]").strip()
        if not domain:
            break
        domains.append(domain)

    domains_file = os.path.join(path, "domains.txt")
    with open(domains_file, "w", encoding="utf-8") as f:
        f.write("\n".join(domains))

    subfinder_file = os.path.join(path, "subfinder.txt")
    subfinder_deep_file = os.path.join(path, "subfinder_deep.txt")
    assetfinder_file = os.path.join(path, "assetfinder.txt")
    crtsh_file = os.path.join(path, "crtsh.txt")

    subfinder_exe = os.path.join(BASE_DIR, "subfinder.exe")
    httpx_exe = os.path.join(BASE_DIR, "httpx.exe")
    assetfinder_exe = os.path.join(BASE_DIR, "assetfinder.exe")
    crtsh_exe = os.path.join(BASE_DIR, "crtsh.exe")

    # Subfinder
    subfinder_lines = run_command_with_spinner(
        f'"{subfinder_exe}" -dL "{domains_file}" -all -silent -o "{subfinder_file}"',
        "Running Subfinder",
        subfinder_file,
    )
    console.print(
        Panel(
            f"[bold green]SUBFINDER FOUND [cyan]{len(subfinder_lines)}[/cyan] UNIQUE SUBDOMAINS.[/bold green]",
            border_style="green",
        )
    )
    send_notification(f"Subfinder Finished. Found {len(subfinder_lines)} Subdomains.")

    # Deep Subfinder
    deep_lines = run_command_with_spinner(
        f'"{subfinder_exe}" -dL "{subfinder_file}" -all -silent -o "{subfinder_deep_file}"',
        "Running Deep Subfinder",
        subfinder_deep_file,
    )
    console.print(
        Panel(
            f"[bold green]DEEP SUBFINDER FOUND [cyan]{len(deep_lines)}[/cyan] UNIQUE SUBDOMAINS.[/bold green]",
            border_style="green",
        )
    )
    send_notification(f"Deep Subfinder Finished. Found {len(deep_lines)} Subdomains.")

    # Assetfinder
    all_assetfinder_results = set()

    for domain in domains:
        temp_output = os.path.join(path, f"assetfinder_{domain}.txt")
        if os.path.exists(temp_output):
            os.remove(temp_output)

        run_command_with_spinner(
            f'"{assetfinder_exe}" --subs-only {domain} > "{temp_output}"',
            f"Running Assetfinder on {domain}",
            temp_output,
        )

        if os.path.exists(temp_output):
            with open(temp_output, "r", encoding="utf-8", errors="ignore") as f:
                lines = set(line.strip() for line in f if line.strip())
                all_assetfinder_results.update(lines)

    # Write final merged assetfinder file
    with open(assetfinder_file, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(all_assetfinder_results)))

    assetfinder_lines = all_assetfinder_results

    console.print(
        Panel(
            f"[bold green]ASSETFINDER FOUND [cyan]{len(assetfinder_lines)}[/cyan] UNIQUE SUBDOMAINS.[/bold green]",
            border_style="green",
        )
    )
    send_notification(
        f"Assetfinder Finished. Found {len(assetfinder_lines)} Subdomains."
    )

    # crt.sh
    crtsh_lines = run_command_with_spinner(
        f'"{crtsh_exe}" -d {" ".join(domains)} > "{crtsh_file}"',
        "Running crt.sh",
        crtsh_file,
    )
    console.print(
        Panel(
            f"[bold green]CRT.SH FOUND [cyan]{len(crtsh_lines)}[/cyan] UNIQUE SUBDOMAINS.[/bold green]",
            border_style="green",
        )
    )
    send_notification(f"Crt.sh Finished. Found {len(crtsh_lines)} Subdomains.")

    # Combine all
    combined_domains = sorted(
        subfinder_lines | deep_lines | assetfinder_lines | crtsh_lines
    )
    combined_file = os.path.join(path, "combined.txt")
    with open(combined_file, "w", encoding="utf-8") as f:
        f.write("\n".join(combined_domains))
    console.print(
        Panel(
            f"[bold green]TOTAL UNIQUE SUBDOMAINS: [cyan]{len(combined_domains)}[/cyan][/bold green]",
            border_style="green",
        )
    )
    send_notification(
        f"All Tools Combined. Total Unique Subdomains: {len(combined_domains)}."
    )

    # httpx 2xx
    httpx_2xx_out = os.path.join(path, "Subdomains_2xx.txt")
    httpx_2xx_lines = run_command_with_spinner(
        f'"{httpx_exe}" -l "{combined_file}" -o "{httpx_2xx_out}" -rl 100 -retries 2 -mc 200',
        "Running httpx 2xx",
        httpx_2xx_out,
    )
    console.print(
        Panel(
            f"[bold green]HTTPX 2XX FOUND [cyan]{len(httpx_2xx_lines)}[/cyan] SUBDOMAINS.[/bold green]",
            border_style="green",
        )
    )
    send_notification(f"Httpx (2xx) Finished. Found {len(httpx_2xx_lines)} Subdomains.")

    # httpx 3xx
    httpx_3xx_out = os.path.join(path, "Subdomains_3xx.txt")
    httpx_3xx_lines = run_command_with_spinner(
        f'"{httpx_exe}" -l "{combined_file}" -o "{httpx_3xx_out}" -rl 100 -retries 2 -mc 301,302',
        "Running httpx 3xx",
        httpx_3xx_out,
    )
    console.print(
        Panel(
            f"[bold green]HTTPX 3XX FOUND [cyan]{len(httpx_3xx_lines)}[/cyan] SUBDOMAINS.[/bold green]",
            border_style="green",
        )
    )
    send_notification(f"Httpx (3xx) Finished. Found {len(httpx_3xx_lines)} Subdomains.")

    # httpx 4xx
    httpx_4xx_out = os.path.join(path, "Subdomains_4xx.txt")
    httpx_4xx_lines = run_command_with_spinner(
        f'"{httpx_exe}" -l "{combined_file}" -o "{httpx_4xx_out}" -rl 100 -retries 2 -mc 403,404',
        "Running httpx 4xx",
        httpx_4xx_out,
    )
    console.print(
        Panel(
            f"[bold green]HTTPX 4XX FOUND [cyan]{len(httpx_4xx_lines)}[/cyan] SUBDOMAINS.[/bold green]",
            border_style="green",
        )
    )
    send_notification(f"Httpx (4xx) Finished. Found {len(httpx_4xx_lines)} Subdomains.")

    # Cleanup Everything Except Subdomains_*xx.txt
    for file in os.listdir(path):
        if not file.startswith("Subdomains_") or not file.endswith("xx.txt"):
            try:
                os.remove(os.path.join(path, file))
            except:
                pass

    # Create Empty Files
    open(os.path.join(path, "notes.txt"), "w").close()
    open(os.path.join(path, "javascript.js"), "w").close()

    console.print(
        Panel(
            "[bold blue]✔ SCAN COMPLETED SUCCESSFULLY![/bold blue]",
            border_style="blue",
            padding=(1, 4),
        )
    )
    send_notification("Subdomains Enumeration Scan Completed.")

    input("\nPress ENTER to exit...")


if __name__ == "__main__":
    main()
