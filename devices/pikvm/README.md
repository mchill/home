# PiKVM Configuration

Copy the files to the PiKVM and restart the kvmd service.

```bash
ssh root@192.168.1.205 rw
scp set_input.py root@192.168.1.205:/root/set_input.py
scp override.yaml root@192.168.1.205:/etc/kvmd/override.yaml
ssh root@192.168.1.205
systemctl restart kvmd
ro
```
