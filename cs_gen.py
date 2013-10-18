import base64, uuid

print base64.b64encode(uuid.uuid4().bytes + 'WithMe' + uuid.uuid4().bytes)
