
import requests

def GET_health():
	services = {"unknown"}
	for service in services:
		r = requests.get(f"http://localhost:5000/{service}")
		status_code = r.status_code
		if status_code < 200 or status_code > 299:
			result = f"service {service} : {status_code}  eror"
			return result
		else:
			result = ""
			for service in services:
				result += f"Service {service} ... 200 ok"
			return result