import base64
from jinja2 import Environment, FileSystemLoader
import os

class Evidence:
    def __init__(self, url, screenshot_bytes, console_logs, network_errors, state_type="SUCCESS", step=0):
        self.url = url
        # Codifica screenshot em Base64 para exibir no HTML
        self.screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        self.console_logs = console_logs
        self.network_errors = network_errors
        self.state_type = state_type # "SUCCESS", "BUG", or "REVISITED"
        self.step = step

class ReportGenerator:
    def __init__(self, output_file="report.html"):
        self.output_file = output_file
        self.evidences = []
        self.edges = []
        self.env = Environment(loader=FileSystemLoader('.'))

    def add_evidence(self, evidence):
        self.evidences.append(evidence)

    def add_edge(self, from_step, to_step, action):
        self.edges.append({"from": from_step, "to": to_step, "action": action})

    def generate(self):
        """Gera o dashboard HTML usando Jinja2."""
        template = self.env.get_template('templates/report_template.html')
        html_content = template.render(evidences=self.evidences, edges=self.edges)

        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"Relatório gerado com sucesso em: {self.output_file}")
