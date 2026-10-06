"""Adapta preview/index.html per publicar-la com a pàgina principal de l'Artifact de prova."""
import re
p = 'preview/index.html'
s = open(p, encoding='utf-8').read()
s = re.sub(r'<!doctype html>\s*', '', s, flags=re.I)
s = re.sub(r'<html[^>]*>\s*<head>', '', s)
for t in ('</head>', '<body>', '</body>', '</html>'):
    s = s.replace(t, '')
s = re.sub(r'<title>[^<]*</title>', '<script>document.documentElement.setAttribute("data-proposta","plafo")</script>\n<title>Nou web UTAC</title>', s, count=1)
open(p, 'w', encoding='utf-8').write(s)
