# reportkit

Builds monthly reports and hands them to an exporter. Exporters are discovered through the
`reportkit.exporters` entry-point group, so a downstream package can register its own.
