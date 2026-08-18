{{- define "persistence.type" -}}
{{- $type := required (printf "persistence: type is required (app %q)" .Values.app) .Values.type -}}
{{- if not (has $type (list "iscsi" "smb")) -}}
{{- fail (printf "persistence: type must be iscsi or smb, got %q (app %q)" $type .Values.app) -}}
{{- end -}}
{{- $type -}}
{{- end -}}

{{- define "persistence.pool" -}}
{{- required (printf "persistence: pool is required (app %q)" .Values.app) .Values.pool -}}
{{- end -}}

{{- define "persistence.storageClass" -}}
{{- $classes := dict "ssdpool" "truenas-iscsi" "hddpool1" "truenas-iscsi-hdd" -}}
{{- $pool := include "persistence.pool" . -}}
{{- $class := index $classes $pool -}}
{{- if not $class -}}
{{- fail (printf "persistence: no iscsi storage class for pool %q (app %q)" $pool .Values.app) -}}
{{- end -}}
{{- $class -}}
{{- end -}}

{{- define "persistence.size" -}}
{{- if eq (include "persistence.type" .) "smb" -}}
{{- default "1Gi" .Values.size -}}
{{- else -}}
{{- required (printf "persistence: size is required for iscsi volumes (app %q)" .Values.app) .Values.size -}}
{{- end -}}
{{- end -}}

{{- define "persistence.source" -}}
{{- printf "//truenas.mchill.lan/%s" .Values.app -}}
{{- end -}}
