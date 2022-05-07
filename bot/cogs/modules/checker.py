from bot.cogs.modules.checker_cielo import cielo
from bot.cogs.modules.checker_erede import erede
from bot.cogs.modules.checker_pagarme import pagarme
from bot.cogs.modules.checker_getnet import getnet
from bot.cogs.modules.external_checker import curl_request
from bot.cogs.modules.checker_mp import mp
from bot.cogs.modules.checker_iugu import iugu
import json, random, time 


def checker(cc):
    try:
        with open('config/config_checker.json', 'r') as file:
            load = json.loads(file.read())
            gate = load['default']
            curl = load['external']
        
        time.sleep(2)

        #if not random.randint(0, 5) == 15:
        if True:
            if gate == 'pagarme':
                check = pagarme(cc)
                #check = [False, 'Transação negada']
            elif gate == 'iugu':
                check = iugu(cc)

            elif gate == 'mercadopago':
                check = mp(cc)

            elif gate == 'cielo':
                check = cielo(cc)

            elif gate == 'erede':
                check = erede(cc)

            elif gate == 'getnet':
                check = getnet(cc)
                
            elif gate == 'external':
                check = curl_request(curl, cc)
            
            else:
                check = [False, 'Nenhum gate selecionado']

            return check
            
        else:
            return [True, 'Transação autorizada - Code: 0000 - R$1,{}'.format(str(random.randint(10, 99)))]

    except:
        return False, 'Erro no arquivo /bot/cogs/modules/checker.py'