settings {
   nodaemon = true,
}

sync {
  default.rsyncssh,
  source = "/libraries/",
  host = "kubernetes@192.168.1.198",
  targetdir = "/volume2/Libraries",
  rsync = {
    _extra = {"-rltvP"},
  },
}
