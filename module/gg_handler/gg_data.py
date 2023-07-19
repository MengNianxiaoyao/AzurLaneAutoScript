import os
from module.config.config import deep_get
from module.base.base import ModuleBase


class GGData(ModuleBase):
    gg_on = False
    gg_enable = False
    gg_auto = False
    ggdata = {}

    def __init__(self, config=None):
        self.config = config
        if not os.path.exists('./gg_config'):
            os.mkdir('./gg_config')
        with open(file=f'./gg_config/{self.config.config_name}.GG.json', mode='a+', encoding='utf-8') as json:
            json.close()
        json = open(file=f'./gg_config/{self.config.config_name}.GG.json', mode='r', encoding='utf-8')
        line = json.readline()
        if line[:-1] != self.config.config_name:
            json.close()
            json = open(file=f'./gg_config/{self.config.config_name}.GG.json', mode='w', encoding='utf-8')
            json.write(f'{self.config.config_name}\n')
            json.write('gg_on=False\n')
            self.ggdata['gg_on'] = False
            self.ggdata['gg_enable'] = deep_get(self.config.data, 'GameManager.GGHandler.Enabled', default=False)
            self.ggdata['gg_auto'] = deep_get(self.config.data, 'GameManager.GGHandler.GGFactorEnable', default=False)
            json.write('gg_enable=' + str(self.ggdata['gg_enable']) + '\n')
            json.write('gg_auto=' + str(self.ggdata['gg_auto']) + '\n')
            json.close()
        else:
            for i in range(3):
                line = json.readline()
                line1, line2 = line.split('=')
                self.ggdata[line1] = True if line2[:-1] == 'True' else False
            json.close()

    def get_data(self):
        # Return a dict of data
        return self.ggdata

    def set_data(self, target=None, value=None):
        self.target = target
        self.value = value
        self.ggdata[self.target] = self.value
        self.update_data()

    def update_data(self):
        with open(file=f'./gg_config/{self.config.config_name}.GG.json', mode='w', encoding='utf-8') as json:
            json.write(f'{self.config.config_name}\n')
            for t in self.ggdata:
                json.write(t + '=' + str(self.ggdata[t]) + '\n')
        json.close()

