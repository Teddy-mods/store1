import requests, random, json, re
from fordev import generators


account_id = '6F34D4C3307A4A3AA823D9E3AD9605C4'
token = '5C6FA9D10E03B9566564924D057E7AA1152E02D456809D18A35935A91FEF4D70'
read_config_file = True

try:
    if read_config_file == True:
        with open('config/config_checker.json', 'r', encoding='UTF-8') as file:
            load = json.loads(file.read())['iugu']
            account_id = load['account_id']
            token = load['token']

except Exception as e:
    print('Erro ao abrir arquivo de configuração:', e)


def people():
    try:
        with open("assets/pessoas.json", "r", encoding="utf8") as f:
            r = json.load(f)
            pessoas = r['pessoa']
            q = len(pessoas)
            pessoa = random.choice(pessoas)

            cpf = pessoa['cpf']
            nome = pessoa['nome']

            return cpf, nome
    except:
        return '00898795702', 'SHIRLEY SAYURI HAMADA TANAKA'


def random_email():
    try:
        with open('assets/db_emails.json', 'r') as file2:
            load = json.loads(file2.read())
            emails = load['emails']
            email = random.choice(emails)
        return email
    except:
        return 'samplemail@gmail.com'


def name_split(nome_completo):
    nome = nome_completo.split()[0]

    s = []
    for n in range(0, len(nome_completo.split())):
        s1 = nome_completo.split()
        if not n == 0:
            s.append(s1[n])

    sobrenome = ' '.join(s)

    return nome, sobrenome


def tokenize_Card(cc, name, proxy=''):
    try:
        ccn, mes, ano, cvv = cc.split("|")

        url = "https://api.iugu.com/v1/payment_token"

        if len(ano) == 2:
            ano = '20'+ano

        nome, sobrenome = name_split(name)
        payload = {
            "account_id": account_id,
            "method": "credit_card",
            "data": {
                "number": ccn,
                "verification_value": cvv,
                "first_name": nome,
                "last_name": sobrenome,
                "month": mes,
                "year": ano
            }
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        if not proxy == '':
            proxy = proxy.lower().replace('https://', '').replace('http://', '').replace('/', '')
            try:
                response = requests.request("POST", url, json=payload, headers=headers, proxies={'http': 'http://'+proxy, 'https': 'http://'+proxy}, verify=False, timeout=20)
            except:
                response = requests.request("POST", url, json=payload, headers=headers)
        else:
            response = requests.request("POST", url, json=payload, headers=headers)

        card_id = response.json()['id']

        return card_id

    except Exception as e:
        print('Erro ao tokenizar cartão:', e)
        return ''


def refund(v_id, proxy=''):
    url = f'https://api.iugu.com/v1/invoices/{v_id}/refund?api_token={token}'

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        if not proxy == '':
            proxy = proxy.lower().replace('https://', '').replace('http://', '').replace('/', '')
            try:
                requests.request("POST", url, headers=headers, proxies={'http': 'http://'+proxy, 'https': 'http://'+proxy}, verify=False, timeout=20)
            except:
                requests.request("POST", url, headers=headers)
        else:
            requests.request("POST", url, headers=headers)
        return True
    except:
        return False


def iugu(cc, proxy=''):
    if len(cc.split("|")) == 4:
        try:
            cpf, nome = people()
            card_id = tokenize_Card(cc, nome, proxy)
            debitar = random.randint(100, 200)
            endereco = generators.people(uf_code=generators.uf()[0], data_only=True)

            url = f"https://api.iugu.com/v1/charge?api_token={token}"

            payload = {
                "payer": {
                    "address": {
                        "street": endereco['endereco'],
                        "number": endereco['numero'],
                        "district": '',
                        "city": endereco['cidade'],
                        "state": endereco['estado'],
                        "zip_code": endereco['cep'],
                        "complement": ''
                    },
                    "cpf_cnpj": cpf,
                    "name": nome,
                    "phone": "+55" + re.sub("[^0-9]+", "", endereco["celular"])
                },
                "items": [
                    {
                        "description": "Check-In",
                        "quantity": 1,
                        "price_cents": debitar
                    }
                ],
                "token": card_id,
                "order_id": str(random.randint(1111111111, 9999999999)),
                "email": random_email()
            }
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            if not proxy == '':
                proxy = proxy.lower().replace('https://', '').replace('http://', '').replace('/', '')
                try:
                    response = requests.request("POST", url, json=payload, headers=headers, proxies={'http': 'http://'+proxy, 'https': 'http://'+proxy}, verify=False, timeout=20)
                except:
                    response = requests.request("POST", url, json=payload, headers=headers)
            else:
                response = requests.request("POST", url, json=payload, headers=headers)

            print(response.text)
            status = response.json()['status']
            transaction_id = response.json()['invoice_id']
            code = response.json()['LR']
            preco = f'R${str(debitar)[0]},{str(debitar)[1]}{str(debitar)[2]}'

            good_returns = ['captured', 'authorized', 'partially_paid', 'in_protest', 'paid', 'pending']

            if status in good_returns:
                refund(transaction_id)
                return True, f'#Aprovado - Transação Capturada - Code: {code} - {preco}'
            else:
                return False, f'#Reprovado - Transação Recusada - Code: {code} - {preco}'

        except Exception as e:
            return False, 'Erro ao criar transação usando o CHK Iugu:', e

    else:
        return False, 'CC inválida. Formato correto: xxxxxxxxxxxxxxxx|xx|xxxx|xxx'