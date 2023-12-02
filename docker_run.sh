docker run -d \
  --name=Nutcase \
  -e TZ=Europe/London \
  -p 9995:9995 \
  -v /home/arthurm/Documents/Software/nut_export/nutcase/config:/config \
  --restart unless-stopped \
  kronos443/nutcase:test
