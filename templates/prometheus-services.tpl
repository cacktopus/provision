{{ with $path := "/prometheus/" }}

{{ range tree $path }}
# {{ $path }}{{ .Key }}
{{ .Value }}
{{ end }}

{{ end }}
