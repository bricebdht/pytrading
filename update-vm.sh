VM_IP=
ssh root@$VM_IP -- rm -rf pytrading || true
ssh root@$VM_IP -- mkdir pytrading
scp -r * root@$VM_IP:pytrading
