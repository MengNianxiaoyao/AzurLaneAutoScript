import uiautomator2 as u2
from module.base.timer import Timer
from module.ui.assets import BACK_ARROW
from module.logger import logger
from module.gg_handler.assets import *
from module.ui.assets import *
from module.meowfficer.assets import *
from module.ocr.ocr import Digit
from module.base.base import ModuleBase as Base
from module.gg_handler.gg_data import GGData

OCR_GG_FOLD = Digit(OCR_GG_FOLD, name='OCR_GG_FOLD', letter=(222, 228, 227), threshold=255)
OCR_GG_FOLD_CHECK = Digit(OCR_GG_FOLD_CHECK, name= 'OCR_GG_FOLD_CHECK', letter=(222, 228, 227), threshold=255)

class GGScreenshot(Base):

    def __init__(self, config, device):
        super().__init__(config, device)
        self.device = device
        self.config = config
        self.d = u2.connect(self.device.serial)
        self.gg_wait_time = self.config.cross_get('GameManager.GGHandler.GGWaitTime')
        self.gg_package_name = self.config.cross_get('GameManager.GGHandler.GGPackageName')
        self.gg_action = self.config.cross_get('GameManager.GGHandler.GGAction')
        self.path = self.config.cross_get('GameManager.GGHandler.GGLuapath')
        self.oldpath = self.config.cross_get('GameManager.GGHandler.GGLuapathRecord')
        self.luapath = "/sdcard/Alarms/Multiplier.lua"

    def skip_error(self):
        """
        Page: 
            in: Game down error
            out: restart
        """
        count = 0
        skipped = 0
        logger.attr('Confirm Time', f'{self.gg_wait_time}s')
        timeout = Timer(0.5, count=self.gg_wait_time).start()
        while 1:
            self.device.sleep(0.5)
            self.device.screenshot()
            if timeout.reached():
                break
            if self.appear_then_click(button=BUTTON_GG_RESTART_ERROR, offset=(50, 50)):
                logger.hr('Game died with GG panel')
                logger.info('Close GG restart error')
                skipped = 1
                count += 1
                if count >= 2:
                    break

        skip_first_screenshot = True
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.sleep(0.5)
                self.device.screenshot()
            if self.appear_then_click(button=BUTTON_GG_RESTART_ERROR, offset=(50, 50)):
                logger.hr('Game died with GG panel')
                logger.info('Close GG restart error')
                skipped = 1
                continue
            if self.appear_then_click(button=BUTTON_GG_SCRIPT_END, offset=(50, 50)):
                logger.info('Close previous script')
                skipped = 1
                continue
            if self.appear_then_click(button=BUTTON_GG_SCRIPT_FATAL, offset=(50, 50)):
                logger.info('Restart previous script')
                skipped = 1
                continue
            if self.appear_then_click(button=BUTTON_GG_APP_CHOOSE, offset=(150, 500)):
                logger.info('APP choose')
                skipped = 1
                continue
            if self.appear(button=BUTTON_GG_SCRIPT_MENU_A, offset=(50, 50)):
                logger.info('Close previous script')
                self.device.click(BUTTON_GG_EXIT_POS)
                skipped = 1
                continue
            if self.appear(button=BUTTON_GG_SEARCH_MODE_CONFIRM, offset=(10, 10), threshold=0.999):
                logger.info('At GG main panel, click GG exit')
                self.device.click(BUTTON_GG_EXIT_POS)
                skipped = 1
                continue
            if self.appear(button=BUTTON_GG_CONFIRM, offset=(50, 50)) and not self.appear(button=BUTTON_GG_CONFIRM, offset=10):
                logger.info('Enter search mode')
                self.device.click(BUTTON_GG_TAB_SEARCH_POS)
                skipped = 1
                continue
            if self.appear(button=BUTTON_GG_CONFIRM, offset=10):
                logger.info('Unexpected GG page, Try GG exit')
                self.device.click(BUTTON_GG_EXIT_POS)
                skipped = 1
                continue
            if not self.appear(button=BUTTON_GG_CONFIRM, offset=(50, 50)):
                logger.hr('GG Panel Disappearance Confirmed')
                if not self.device.app_is_running():
                    self.device.app_start()
                else:
                    logger.info('Game is already running')
                self._gg_exit()
                break
        return skipped

    def _enter_gg(self):
        """
        Page:
            in: any
            out: any GG
        """
        skip_first_screenshot = True
        method = [
            REWARD_GOTO_MAIN,
            GOTO_MAIN,
            MAIN_GOTO_BUILD,
            DORM_CHECK,
            MEOWFFICER_FORT_ENTER
        ]
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.sleep(0.5)
                self.device.screenshot()
            if self.appear_then_click(button=BUTTON_GG_START, offset=(50, 50)):
                continue
            if self.appear(button=BUTTON_GG_ENTER, offset=(50, 50)) or self.appear(button=BUTTON_GG_CONFIRM, offset=(50, 50)):
                logger.hr('Enter GG')
                logger.info('Entered GG')
                break
            for i in range(len(method)):
                if self.appear(button=method[int(i)], offset=(50, 50)):
                    self.device.click(BUTTON_GG_ENTER_POS)
                    break

        skip_first_screenshot = True
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.sleep(0.5)
                self.device.screenshot()
            if not self.appear(button=BUTTON_GG_APP_CHOOSE, offset=(150, 500)):
                self.device.click(BACK_ARROW)
                logger.info('Actually APP choosing button')
            else:
                self.appear_then_click(button=BUTTON_GG_APP_CHOOSE, offset=(150, 500))
                logger.info('APP Choose')
                break

    def _gg_enter_script(self):
        """
        Page:
            in: any GG
            out: GG ready to start script
        """
        skip_first_screenshot = True
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.sleep(0.5)
                self.device.screenshot()
            if self.appear(button=BUTTON_GG_SCRIPT_ENTER_CONFIRM, offset=(50, 50)):
                logger.hr('Lua execute')
                break
            elif self.appear_then_click(button=BUTTON_GG_SCRIPT_END, offset=(50, 50)):
                logger.info('Close previous script')
            elif self.appear_then_click(button=BUTTON_GG_SCRIPT_FATAL, offset=(50, 50)):
                logger.info('Stop previous script')
            elif self.appear_then_click(button=BUTTON_GG_APP_CHOOSE, offset=(150, 500)):
                logger.info('APP choose')
            elif self.appear(button=BUTTON_GG_SEARCH_MODE_CONFIRM, offset=(10, 10), threshold=0.95):
                self.device.click(BUTTON_GG_SCRIPT_ENTER_POS)
                logger.info('Enter script choose')
                self._gg_lua()
            else:
                self.device.click(BUTTON_GG_TAB_SEARCH_POS)
                logger.info('Enter search mode')

        skip_first_screenshot = True
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.sleep(0.5)
                self.device.screenshot()
            if self.appear_then_click(button=BUTTON_GG_SCRIPT_START, offset=(50, 50)):
                return 1

    def _gg_mode(self):
        """
        Page:
            in: GG Script Menu
            out: GG GG input panel
        """
        skip_first_screenshot = True
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.sleep(0.5)
                self.device.screenshot()
            if self.appear(button=BUTTON_GG_SCRIPT_MENU_A, offset=(50, 50), threshold=0.8):
                method = [BUTTON_GG_SCRIPT_MENU_B, BUTTON_GG_SCRIPT_MENU_A]
                self.device.click(method[int(self._mode)])
                break

    def _gg_handle_factor(self):
        """
        Page:
            in: GG input panel
            out:factor set(Not ensured yet)
        """
        method = [
            BUTTON_GG_SCRIPT_PANEL_NUM0,
            BUTTON_GG_SCRIPT_PANEL_NUM1,
            BUTTON_GG_SCRIPT_PANEL_NUM2,
            BUTTON_GG_SCRIPT_PANEL_NUM3,
            BUTTON_GG_SCRIPT_PANEL_NUM4,
            BUTTON_GG_SCRIPT_PANEL_NUM5,
            BUTTON_GG_SCRIPT_PANEL_NUM6,
            BUTTON_GG_SCRIPT_PANEL_NUM7,
            BUTTON_GG_SCRIPT_PANEL_NUM8,
            BUTTON_GG_SCRIPT_PANEL_NUM9,
        ]
        self.wait_until_appear(button=BUTTON_GG_SCRIPT_START_PROCESS, skip_first_screenshot=True)
        logger.hr('Factor Input')
        if (isinstance(self._factor, int) == True or isinstance(self._factor, float) == True) and (1 <= self._factor <= 1000):
            logger.attr('Factor', self._factor)
            self.device.sleep(0.5)
            self.device.screenshot()
            FOLD = OCR_GG_FOLD.ocr(self.device.image)
            if self._factor == int(FOLD):
                logger.hr('Re: Input')
                logger.info('Skip factor input')
                logger.hr('Factor Check')
                logger.info('Skip factor check')
                return 0
            logger.hr('Re: Input')
            logger.info('Factor Reinput')
            for i in str(self._factor):
                self.appear_then_click(button=method[int(i)], offset=(50, 50))
                self.device.sleep(0.5)
            logger.info('Input success')
            logger.hr('Factor Check')
            count=0
            while 1:
                self.device.screenshot()
                FOLD_CHECK = OCR_GG_FOLD_CHECK.ocr(self.device.image)
                if self._factor == FOLD_CHECK:
                    logger.info('Check success')
                    break
                else:
                    count+=1
                    logger.warning('Check error')  
                    logger.info('Factor delete')
                    self.device.long_click(button=BUTTON_GG_SCRIPT_PANEL_DEL, duration=(1, 1))
                    if count>=3:
                        logger.error('Check more failed,Try default factor will be run')
                        for i in str(200):
                            self.appear_then_click(button=method[int(i)], offset=(50, 50))
                            self.device.sleep(0.5)
                        break
                    logger.info('Input again')
                    for i in str(self._factor):
                        self.appear_then_click(button=method[int(i)], offset=(50, 50))
                        self.device.sleep(0.5)
                    self.device.sleep(0.5)
        else:
            for i in range(3):
                logger.error('Factor illegal')
            logger.warning('Try default factor will be run')
            from module.notify import handle_notify
            handle_notify(self.config.Error_OnePushConfig,
                          title=f"Alas <{self.config.config_name}> 输入的倍率不合法",
                          content=f"<{self.config.config_name}> 需要手动介入，输入的倍率不合法，将尝试默认倍率运行")
            logger.hr('Try again')
            for i in str(200):
                self.appear_then_click(button=method[int(i)], offset=(50, 50))
                self.device.sleep(0.5)
        logger.hr('GG Exit')

    def _gg_script_run(self):
        """
        Page:
            in: GG factor set
            out: GG Menu
        """
        logger.hr('Execute')
        skip_first_screenshot = True
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.sleep(0.5)
                self.device.screenshot()
            if self.appear_then_click(button=BUTTON_GG_SCRIPT_START_PROCESS, offset=(50, 50), threshold=0.9):
                self.device.sleep(0.5)
                self.device.screenshot()
                if not self.appear(button=BUTTON_GG_SCRIPT_START_PROCESS, offset=(50, 50), threshold=0.9):
                    break
                else:
                    self.device.click(BUTTON_GG_SCRIPT_START_PROCESS)
                    break
        logger.info('Waiting for end')

        skip_first_screenshot = True
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.sleep(0.5)
                self.device.screenshot()
            if self.appear_then_click(button=BUTTON_GG_SCRIPT_END, offset=(50, 50), threshold=0.9):
                return 1
    
    def _gg_exit(self):
        if (self.gg_action == 'auto' and self.gg_package_name != 'com.') or (self.gg_action == 'manual' and self.gg_package_name != 'com.'):
            self.d.app_stop(f'{self.gg_package_name}')
            logger.info('GG kill')

    def _gg_start(self):
        if (self.gg_action == 'auto' and self.gg_package_name != 'com.') or (self.gg_action == 'manual' and self.gg_package_name != 'com.'):
            self.d.app_start(f'{self.gg_package_name}')
            logger.hr('GG start')
            skip_first_screenshot = True
            while 1:
                if skip_first_screenshot:
                    skip_first_screenshot = False
                else:
                    self.device.sleep(0.5)
                    self.device.screenshot()
                if self.appear_then_click(button=BUTTON_GG_SKIP0, offset=(50, 50)):
                    self.device.sleep(1)
                    continue
                if self.appear_then_click(button=BUTTON_GG_SKIP1, offset=(50, 50)):
                    self.device.sleep(1)
                    continue
                if self.appear_then_click(button=BUTTON_GG_START, offset=(50, 50)):
                    self.device.sleep(1)
                    self.device.screenshot()
                    if self.appear_then_click(button=BUTTON_GG_START, offset=(50, 50)):
                        self.device.sleep(1)
                        self.device.screenshot()
                        if not self.appear(button=BUTTON_GG_START, offset=(50, 50)):
                            break
                        else:
                            self.device.click(BUTTON_GG_START)
                            break
                    else:
                        break
            self.device.sleep(self.gg_wait_time)

    def _gg_lua(self):
        if self.path != "" and self.gg_action == 'manual' and self.gg_package_name != 'com.':
            self.luapath = self.path
        if self.oldpath == False:
            logger.hr('Lua path set')
            self.d.send_keys(f"{self.luapath}")
            logger.info('Lua path set success')
            self.config.cross_set('GameManager.GGHandler.GGLuapathRecord', value=True)
        else:
            logger.hr('Skip lua path set')
        if self.gg_action == 'auto' and self.gg_package_name != 'com.':
            self.device.sleep(self.gg_wait_time)
            self.device.screenshot()
            if not self.appear(button=OCR_GG_LUAPATH, offset=(50, 50)):
                logger.warning("Lua path error")
                self.device.click(button=BUTTON_GG_LUACHOOSE)
                self.device.sleep(1)
                for i in range(2):
                    self.device.sleep(0.5)
                    self.device.click(BUTTON_GG_BACK)
                skip_first_screenshot = True
                while 1:
                    if skip_first_screenshot:
                        skip_first_screenshot = False
                    else:
                        self.device.sleep(0.5)
                        self.device.screenshot()
                    if self.appear_then_click(button=BUTTON_GG_PATH0, offset=(50, 50)):
                        continue
                    if self.appear_then_click(button=BUTTON_GG_PATH1, offset=(50, 50)):
                        continue
                    if self.appear_then_click(button=BUTTON_GG_LUA, offset=(50, 50)):
                        return 1

    def gg_push(self):
        if self.oldpath == False:
            logger.hr('Push lua file')
            self.device.adb_push('bin/lua/Multiplier.lua', f"{self.luapath}")
            logger.info('Push success')
        else:
            logger.hr('Skip push lua file')

    def run(self, mode=True, factor=200):
        self._mode = mode
        self._factor = factor
        self._gg_start()
        self._enter_gg()
        self._gg_enter_script()
        self._gg_mode()
        self._gg_handle_factor()
        self._gg_script_run()
        GGData(self.config).set_data(target='gg_on', value=self._mode)
        self.skip_error()
        logger.attr('GG', 'Enabled')
        logger.hr('GG panel closed')
        self._gg_exit()