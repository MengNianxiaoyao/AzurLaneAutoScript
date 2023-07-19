from module.base.timer import timeout, Timer
from module.base.base import ModuleBase as Base
from module.gg_handler.gg_data import GGData
from module.gg_handler.gg_screenshot import GGScreenshot
# from module.gg_handler.gg_u2 import GGU2
from module.logger import logger
from module.notify import handle_notify
from module.gg_handler.assets import OCR_PRE_BATTLE_CHECK
from module.ocr.ocr import Digit
from module.gg_handler.gg_task import *

OCR_CHECK = Digit(OCR_PRE_BATTLE_CHECK, name='OCR_PRE_BATTLE_CHECK', letter=(255, 255, 255), threshold=255)

class GGHandler(Base):
    """
    A module to handle needs of cheaters
    Args:
        config: AzurLaneConfig
        device: Device
    """

    def __init__(self, config, device):
        self.config = config
        self.device = device
        self.factor = self.config.cross_get('GameManager.GGHandler.GGMultiplyingFactor', default=200)
        self.method = self.config.cross_get('GameManager.GGHandler.GGMethod', default='screenshot')
        # self.gg_package_name = self.config.cross_get('GameManager.GGHandler.GGPackageName')

    def restart(self, crashed=False):
        from module.handler.login import LoginHandler
        from module.exception import GameStuckError
        _crashed = crashed
        for _ in range(2):
            try:
                # if _crashed:
                #     timeout(self.handle_u2_restart, timeout_sec=60)
                if not timeout(LoginHandler(self.config, self.device).app_restart, timeout_sec=600):
                    break
                raise RuntimeError
            except GameStuckError as e:
                pass
            except Exception as e:
                logger.exception(e)
                if _crashed:
                    from module.notify import handle_notify
                    handle_notify(self.config.Error_OnePushConfig,
                                  title=f"Alas <{self.config.config_name}> 崩溃了",
                                  content=f"<{self.config.config_name}> 需要手动介入，也许你的模拟器卡死")
                    exit(1)
                _crashed = True

    def set(self, mode=True):
        """
            Set the GG status to True/False.
            Args:
                mode: bool
        """
        logger.hr('Enabling GG', level=2)
        if mode:
            GGScreenshot(config=self.config, device=self.device).run(mode=True, factor=self.factor)
            # if self.method == 'screenshot' or self.gg_package_name == 'com.':
            #     GGScreenshot(config=self.config, device=self.device).gg_set(mode=True, factor=self.factor)
            # elif self.method == 'u2':
            #     self.handle_u2_restart()
            #     success = timeout(GGU2(config=self.config, device=self.device).set_on, timeout_sec=120, factor=self.factor)
            #     if success:
            #         from module.exception import GameStuckError
            #         raise GameStuckError
        else:
            self.gg_reset()

    def skip_error(self) -> bool:
        """
        Close all the windows of GG.
        Often to be used when game restarts with GG enabled.
        Returns:
            bool: Whether GG error panel occurs
        """
        return GGScreenshot(config=self.config, device=self.device).skip_error()
        # if self.method == 'screenshot' or self.gg_package_name == 'com.':
        #     return GGScreenshot(config=self.config, device=self.device).skip_error()
        # elif self.method == 'u2':
        #     return GGU2(config=self.config, device=self.device).skip_error()

    def check_config(self) -> dict:
        """
        Reset GG config to the user's config and return gg_data.
        Returns:
            gg_data: dict = {
                        'gg_enable' : bool = Whether GG manager enabled,
                        'gg_auto' : bool = Whether to start GG before tasks,
                        'gg_on' : bool = Whether multiplier is on now}
        """
        gg_enable = self.config.cross_get('GameManager.GGHandler.Enabled', default=False)
        gg_auto = self.config.cross_get('GameManager.GGHandler.GGFactorEnable', default=False)
        GGData(self.config).set_data(target='gg_enable', value=gg_enable)
        GGData(self.config).set_data(target='gg_auto', value=gg_auto)
        gg_data = GGData(self.config).get_data()
        logger.hr('Check GG config')
        logger.info(f'GG config:')
        logger.info(
            f'[Enabled={gg_data["gg_enable"]}] [AutoRestart={gg_data["gg_auto"]}] [CurrentStage={gg_data["gg_on"]}]')
        return gg_data

    # def handle_u2_restart(self):
    #     _need_restart_atx = self.config.cross_get('GameManager.GGHandler.RestartATX')
    #     if self.method == 'u2' and _need_restart_atx:
    #         try:
    #             timeout(self.device.restart_atx, 60)
    #         except Exception:
    #             from module.notify import handle_notify
    #             handle_notify(self.config.Error_OnePushConfig,
    #                           title=f"Alas <{self.config.config_name}> 模拟器出错",
    #                           content=f"<{self.config.config_name}> 需要手动介入，也许你的模拟器卡死")
    #             exit(1)
    #         import uiautomator2 as u2
    #         logger.info('Reset uiautomator')
    #         try:
    #             u2.connect(self.device.serial).reset_uiautomator()
    #         except Exception:
    #             from module.notify import handle_notify
    #             handle_notify(self.config.Error_OnePushConfig,
    #                           title=f"Alas <{self.config.config_name}> 重启u2服务失败",
    #                           content=f"<{self.config.config_name}> 需要手动介入，也许你的模拟器卡死")
    #             exit(1)

    def handle_restart(self):
        """
        Handle the restart errors of GG.
        """
        gg_data = GGData(config=self.config).get_data()
        gg_enable = gg_data['gg_enable']
        if gg_enable:
            GGData(config=self.config).set_data(target='gg_on', value=False)
            logger.hr('Loading GG config')
            logger.info(f'GG config:')
            logger.info(
                f'[Enabled={gg_data["gg_enable"]}] [AutoRestart={gg_data["gg_auto"]}] [CurrentStage={gg_data["gg_on"]}]')
            if not self.skip_error():
                logger.hr('Assume game died without GG panel')

    def gg_reset(self):
        """
        Force restart the game to reset GG status to False
        """
        gg_data = GGData(self.config).get_data()
        if gg_data['gg_enable'] and gg_data['gg_on']:
            logger.hr('Disabling GG', level=2)
            self.restart()
            logger.attr('GG', 'Disabled')

    def check_status(self, mode=True):
        """
        A check before a task begins to decide whether to enable GG and set it.
        Args:
            mode: The multiplier status when finish the check.
        """
        gg_data = GGData(self.config).get_data()
        if gg_data['gg_enable']:
            gg_auto = mode if self.config.cross_get('GameManager.GGHandler.GGFactorEnable', default=False) else False
            logger.hr('Check GG status')
            logger.info(f'Check GG status:')
            logger.info(
                f'[Enabled={gg_data["gg_enable"]}] [AutoRestart={gg_data["gg_auto"]}] [CurrentStage={gg_data["gg_on"]}]')
            if gg_auto:
                if not gg_data['gg_on']:
                    self.set(True)
            elif gg_data['gg_on']:
                self.gg_reset()

    def power_limit(self, task=''):
        """
        Forced final check before some dangerous tasks for cheaters.
        If power is too high, disable the multiplier and assume the user need GG to be Enabled before the other tasks.
        Args:
            task: str = What task it is to limit power, default limit is 16500 for front ships.
        """
        limit = self.config.cross_get(f'GameManager.PowerLimit.{task}', default=16500)
        logger.attr('Power Limit', limit)
        skip_first_screenshot = True
        timeout = Timer(1, count=15).start()
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.sleep((1.5, 2))
                self.device.screenshot()

            if timeout.reached():
                logger.error('Get ScoutCE timeout')
                handle_notify(self.config.Error_OnePushConfig,
                            title=f"Alas <{self.config.config_name}> 超时",
                            content=f"<{self.config.config_name}> 识别战力超时，模拟器卡死或者网络掉线")
                exit(1)
            ocr = OCR_CHECK.ocr(self.device.image)
            if ocr > 1000:
                break
        if ocr >= limit:
            for i in range(3):
                logger.critical('There\'s high chance that GG is on, restart to disable it')
            handle_notify(self.config.Error_OnePushConfig,
                              title=f"Alas <{self.config.config_name}> 超模战力",
                              content=f"<{self.config.config_name}> 识别到使用超模战力进行不被允许的任务，紧急重启规避检查")
            GGData(self.config).set_data(target='gg_on', value=False)
            GGData(self.config).set_data(target='gg_enable', value=True)
            self.config.cross_set('GameManager.GGHandler.Enabled', value=True)
            self.config.cross_set('GameManager.GGHandler.GGFactorEnable', value=True)
            return True

    def handle_restart_before_tasks(self) -> bool:
        """
        Check if user need to restart everytime alas starts before tasks, and handle it.
        Returns:
            bool: If it needs restart first
        """
        gg_data = GGData(self.config).get_data()
        if (self.config.cross_get('GameManager.GGHandler.RestartEverytime', default=True) and gg_data['gg_enable']):
            logger.info('Restart to reset GG status.')
            self.restart()
            return True
        return False

    def check_then_set_gg_status(self, task=''):
        """
        If task is in list _disabled or _group_enabled defined in this function,
        set gg to the defined status
        Args:
            task : str = the next task to run
        """
        _disabled_task = self.config.cross_get('GameManager.GGHandler.DisabledTask')
        """
            'disable_guild_and_dangerous'
            'disable_all_dangerous_task'
            'disable_meta_and_exercise'
            'disable_exercise'
            'enable_all'
        """

        _group_exercise = EXERCISE
        _group_meta = META
        _group_coalition = COALITION
        _group_raid = RAID
        _group_personal_choice = GUILD
        _group_enabled = MAINS + EVENTS + FARM + DAYIL + OPSI + OTHER

        # Handle ignorance

        if _disabled_task == 'disable_guild_and_dangerous':
            _disabled = _group_exercise + _group_meta + _group_raid + _group_coalition + _group_personal_choice
            _enabled = _group_enabled
        elif _disabled_task == 'disable_all_dangerous_task':
            _disabled = _group_exercise + _group_meta + _group_raid + _group_coalition
            _enabled = _group_enabled + _group_personal_choice
        elif _disabled_task == 'disable_meta_and_exercise':
            _disabled = _group_exercise + _group_meta
            _enabled = _group_enabled + _group_raid + _group_coalition + _group_personal_choice
        elif _disabled_task == 'disable_exercise':
            _disabled = _group_exercise
            _enabled = _group_enabled + _group_personal_choice + _group_raid + _group_coalition + _group_meta
        elif _disabled_task == 'enable_all':
            _disabled = []
            _enabled = _group_enabled + _group_personal_choice + _group_raid + _group_coalition + _group_meta + _group_exercise

        if task in _disabled:
            self.check_status(False)
        elif task in _enabled:
            self.check_status(True)
