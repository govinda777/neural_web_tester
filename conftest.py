import sys
import os

# Adiciona a pasta 'src' ao sys.path para permitir que os testes encontrem os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
