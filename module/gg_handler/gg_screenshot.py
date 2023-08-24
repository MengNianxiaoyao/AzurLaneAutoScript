import uiautomator2 as u2
from module.base.timer import Timer
from module.handler.assets import LOGIN_CHECK
from module.gg_handler.assets import *
from module.ui.assets import *
from module.meowfficer.assets import *
from module.ocr.ocr import Digit
from module.logger import logger
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
        self.method = [
            REWARD_GOTO_MAIN,
            GOTO_MAIN,
            MAIN_GOTO_BUILD,
            DORM_CHECK,
            MEOWFFICER_FORT_ENTER
            ]
        self.choose = [
            BUTTON_GG_APP_CHOOSE0,
            BUTTON_GG_APP_CHOOSE1,
            BUTTON_GG_APP_CHOOSE2
        ]

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
            if self.appear_then_click(BUTTON_GG_RESTART_ERROR, offset=(50, 50)):
                logger.hr('Game died with GG panel')
                logger.info('Close GG restart error')
                skipped = 1
                count += 1
                if count >= 1:
                    break

        skip_first_screenshot = True
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.sleep(0.5)
                self.device.screenshot()
            if self.appear_then_click(BUTTON_GG_RESTART_ERROR, offset=(50, 50)):
                logger.hr('Game died with GG panel')
                logger.info('Close GG restart error')
                skipped = 1
                continue
            if self.appear_then_click(BUTTON_GG_SCRIPT_END, offset=(50, 50)):
                logger.info('Close previous script')
                skipped = 1
                continue
            if self.appear_then_click(BUTTON_GG_SCRIPT_FATAL, offset=(50, 50)):
                logger.info('Restart previous script')
                skipped = 1
                continue
            if self.appear_then_click(BUTTON_GG_APP_CHOOSE0, offset=(50, 50)):
                logger.info('APP choose')
                skipped = 1
                continue
            if self.appear_then_click(BUTTON_GG_APP_CHOOSE1, offset=(50, 50)):
                logger.info('APP Choose')
                continue
            if self.appear(BUTTON_GG_SCRIPT_MENU_A, offset=(50, 50)):
                logger.info('Close previous script')
                self.device.click(BUTTON_GG_EXIT_POS)
                skipped = 1
                continue
            if self.appear(BUTTON_GG_SEARCH_MODE_CONFIRM, offset=(10, 10), threshold=0.999):
                logger.info('At GG main panel, click GG exit')
                self.device.click(BUTTON_GG_EXIT_POS)
                skipped = 1
                continue
            if self.appear_then_click(BUTTON_GG_ERROR_ENTER, offset=(50, 50)):
                skipped = 1
                continue
            if self.appear(BUTTON_GG_CONFIRM, offset=(50, 50)) and not self.appear(BUTTON_GG_CONFIRM, offset=(10, 10)):
                logger.info('Enter search mode')
                self.device.click(BUTTON_GG_TAB_SEARCH_POS)
                skipped = 1
                continue
            if self.appear(BUTTON_GG_CONFIRM, offset=(10, 10)):
                logger.info('Unexpected GG page, Try GG exit')
                self.device.click(BUTTON_GG_EXIT_POS)
                skipped = 1
                continue
            if not self.appear(BUTTON_GG_CONFIRM, offset=(50, 50)):
                logger.hr('GG Panel Disappearance Confirmed')
                if not self.device.app_is_running():
                    self.device.app_start()
                else:
                    logger.info('Game is already running')
                self.gg_exit()
                break
        return skipped

    def _enter_gg(self):
        """
        Page:
            in: any
            out: any GG
        """
        skip_first_screenshot = True
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.sleep(0.5)
                self.device.screenshot()
            if self.appear_then_click(LOGIN_CHECK, offset=(30, 30)):
                continue
            if self.appear(BUTTON_GG_CONFIRM, offset=(50, 50)):
                logger.hr('Enter GG')
                logger.info('Entered GG')
                break
            for i in range(len(self.method)):
                if self.appear(self.method[int(i)], offset=(50, 50)):
                    self.device.click(BUTTON_GG_ENTER_POS)
                    break

    def enter_gg(self):
        self._enter_gg()
        skip_first_screenshot = True
        logger.hr('Enter APP State')
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.sleep(0.5)
                self.device.screenshot()
            for i in range(len(self.choose)):
                if self.appear_then_click(self.choose[int(i)], offset=(50, 50)):
                    logger.info('APP Choose')
                    break
                if i == range(len(self.choose)):
                    self.device.sleep(0.5)
                    self.device.screenshot()
            if self.appear(BUTTON_GG_STOP, offset=(50, 50)):
                logger.hr('GG Restart')
                self.gg_exit()
                self.gg_push()
                self.gg_start()
                self._enter_gg()
                continue
            if self.appear(BUTTON_GG_APP_ENTER, offset=(50, 50)) and \
                BUTTON_GG_APP_ENTER.match_appear_on(self.device.image):
                logger.info('APP Enter')
                break
            if not self.appear(BUTTON_GG_APP_ENTER, offset=(50, 50), threshold=0.999) and \
                self.appear(BUTTON_GG_SEARCH_MODE_CONFIRM, offset=(10, 10), threshold=0.999):
                logger.info('Reselect APP')
                self.device.click(BUTTON_GG_RECHOOSE)
                continue

    def _gg_enter_script(self):
        """
        Page:
            in: any GG
            out: GG ready to start script
        """
        logger.hr('Select Script')
        skip_first_screenshot = True
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.sleep(0.5)
                self.device.screenshot()
            if self.appear_then_click(BUTTON_GG_STOP, offset=(50, 50)):
                logger.hr('GG Restart')
                self.gg_exit()
                self.gg_push()
                self.gg_start()
                self.enter_gg()
                continue
            if self.appear_then_click(BUTTON_GG_SCRIPT_END, offset=(50, 50)):
                continue 
            if self.appear(BUTTON_GG_SCRIPT_ENTER_CONFIRM, offset=(50, 50)):
                self.gg_lua()
                logger.hr('Lua execute')
                break
            for i in range(len(self.choose)):
                if self.appear_then_click(self.choose[int(i)], offset=(50, 50)):
                    logger.info('APP Choose')
                    break
                if i == range(len(self.choose)):
                    self.device.sleep(0.5)
                    self.device.screenshot()
            if self.appear_then_click(BUTTON_GG_SCRIPT_END, offset=(50, 50)):
                logger.info('Close previous script')
                continue
            if self.appear_then_click(BUTTON_GG_SCRIPT_FATAL, offset=(50, 50)):
                logger.info('Stop previous script')
                continue
            if self.appear(BUTTON_GG_SEARCH_MODE_CONFIRM, offset=(10, 10)) and \
                BUTTON_GG_SEARCH_MODE_CONFIRM.match_appear_on(self.device.image):
                self.device.click(BUTTON_GG_SCRIPT_ENTER_POS)
                logger.info('Enter script choose')
                continue
            if not self.appear(BUTTON_GG_SEARCH_MODE_CONFIRM, offset=(10, 10), threshold=0.999):
                self.device.click(BUTTON_GG_TAB_SEARCH_POS)
                logger.info('Enter search mode')
                continue

    def gg_enter_script(self):
        self._gg_enter_script()
        skip_first_screenshot = True
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.sleep(0.5)
                self.device.screenshot()
            if self.appear(BUTTON_GG_SEARCH_MODE_CONFIRM, offset=(10, 10)) and \
                BUTTON_GG_SEARCH_MODE_CONFIRM.match_appear_on(self.device.image):
                self.device.click(BUTTON_GG_SCRIPT_ENTER_POS)
            if self.appear_then_click(BUTTON_GG_SCRIPT_START, offset=(50, 50)):
                continue
            if self.appear_then_click(BUTTON_GG_ERROR_ENTER, offset=(50, 50)):
                self._gg_enter_script()
                continue
            if self.appear(BUTTON_GG_SCRIPT_MENU_A, offset=(50, 50)):
                logger.info('Revise mode')
                break

    def gg_mode(self):
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
            if self.appear_then_click(BUTTON_GG_STOP, offset=(50, 50)):
                logger.hr('GG Restart')
                self.gg_exit()
                self.gg_push()
                self.gg_start()
                self.enter_gg()
                self.gg_enter_script()
                continue
            if self.appear_then_click(BUTTON_GG_SCRIPT_END, offset=(50, 50)):
                continue
            if self.appear_then_click(BUTTON_GG_SCRIPT_MENU_A, offset=(50, 50)):
                continue
            if self.appear(BUTTON_GG_SCRIPT_START_PROCESS, offset=(50, 50)):
                break

    def gg_handle_factor(self):
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
        self.wait_until_appear(BUTTON_GG_SCRIPT_START_PROCESS, skip_first_screenshot=True)
        logger.hr('Factor Input')
        if (isinstance(self.factor, int) == True or isinstance(self.factor, float) == True) and (1 <= self.factor <= 1000):
            logger.attr('Factor', self.factor)
            while 1:
                self.device.sleep(0.5)
                self.device.screenshot()
                FOLD = OCR_GG_FOLD.ocr(self.device.image)
                if FOLD != None:
                    break
            if self.factor == int(FOLD):
                logger.hr('Re: Input')
                logger.info('Skip factor input')
                logger.hr('Factor Check')
                logger.info('Skip factor check')
                return 1
            logger.hr('Re: Input')
            logger.info('Factor Reinput')
            for i in str(self.factor):
                self.appear_then_click(method[int(i)], offset=(50, 50), interval=1)
            logger.info('Input success')
            logger.hr('Factor Check')
            count=0
            while 1:
                self.device.sleep(0.5)
                self.device.screenshot()
                FOLD_CHECK = OCR_GG_FOLD_CHECK.ocr(self.device.image)
                if self.factor == FOLD_CHECK:
                    logger.info('Check success')
                    break
                else:
                    count += 1
                    logger.warning('Check error')  
                    logger.info('Factor delete')
                    self.device.long_click(BUTTON_GG_SCRIPT_PANEL_DEL, duration=(1, 1.1))
                    if count >= 3:
                        logger.error('Check more failed,Try default factor will be run')
                        for i in str(200):
                            self.appear_then_click(method[int(i)], offset=(50, 50), interval=1)
                        break
                    logger.info('Input again')
                    for i in str(self.factor):
                        self.appear_then_click(method[int(i)], offset=(50, 50), interval=1)
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
                self.appear_then_click(method[int(i)], offset=(50, 50), interval=1)
                
        logger.hr('GG Exit')

    def _gg_script_run(self):
        logger.hr('Execute')
        skip_first_screenshot = True
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.sleep(0.5)
                self.device.screenshot()
            if self.appear_then_click(BUTTON_GG_SCRIPT_START_PROCESS, offset=(50, 50)):
                continue
            if self.appear(BUTTON_GG_SCRIPT_START_CHECK, offset=(50, 50)):
                break
        logger.info('Waiting for end')

    def gg_script_run(self):
        """
        Page:
            in: GG factor set
            out: GG Menu
        """
        self._gg_script_run()
        skip_first_screenshot = True
        count = 0
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.sleep(0.5)
                self.device.screenshot()
            for i in range(len(self.method)):
                if self.appear(self.method[int(i)], offset=(50, 50), threshold=0.999):
                    self.device.click(BUTTON_GG_ENTER_POS)
                    break
            if self.appear_then_click(BUTTON_GG_ERROR_ENTER, offset=(50, 50)):
                logger.hr('GG Restart')
                self.gg_exit()
                self.gg_push()
                self.gg_start()
                self.enter_gg()
                self.gg_enter_script()
                self.gg_mode()
                self.gg_handle_factor()
                self._gg_script_run()
                continue
            if self.appear_then_click(BUTTON_GG_SCRIPT_END, offset=(50, 50)):
                count += 1
                continue
            if self.appear(BUTTON_GG_SEARCH_MODE_BUTTON, offset=(50, 50)) and count != 0:
                return 1
    
    def gg_exit(self):
        if (self.gg_action == 'auto' and self.gg_package_name != 'com.') or (self.gg_action == 'manual' and self.gg_package_name != 'com.'):
            self.d.app_stop(f'{self.gg_package_name}')
            logger.info('GG kill')

    def gg_start(self):
        if (self.gg_action == 'auto' and self.gg_package_name != 'com.') or (self.gg_action == 'manual' and self.gg_package_name != 'com.'):
            self.d.app_start(f'{self.gg_package_name}')
            logger.hr('GG start')
            skip_first_screenshot = True
            count = 0
            while 1:
                if skip_first_screenshot:
                    skip_first_screenshot = False
                else:
                    self.device.sleep(0.5)
                    self.device.screenshot()
                if self.appear_then_click(BUTTON_GG_SCRIPT_END, offset=(50, 50)):
                    continue
                if self.appear_then_click(BUTTON_GG_SKIP0, offset=(50, 50)):
                    count += 1
                    continue
                if self.appear_then_click(BUTTON_GG_SKIP1, offset=(50, 50)):
                    count += 1
                    continue
                if self.appear(BUTTON_GG_ENTER, offset=(50, 50)):
                    self.device.click(BUTTON_GG_EXIT_POS)
                    count += 1
                    continue
                if self.appear(BUTTON_GG_CONFIRM, offset=(50, 50)):
                    self.device.click(BUTTON_GG_EXIT_POS)
                    count += 1
                    continue
                if self.appear_then_click(BUTTON_GG_START, offset=(50, 50)):
                    count += 1
                    continue
                for i in range(len(self.method)):
                    if self.appear(self.method[int(i)], offset=(50, 50)) and count != 0:
                        return 1

    def gg_lua(self):
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
            while 1:
                self.device.sleep(0.5)
                self.device.screenshot()
                if not self.appear(OCR_GG_LUAPATH, offset=(50, 50)) and self.appear(BUTTON_GG_LUACHOOSE, offset=(50, 50)):
                    break
                if self.appear(OCR_GG_LUAPATH, offset=(50, 50)):
                    return 1

            logger.warning("Lua path error")
            self.device.click(BUTTON_GG_LUACHOOSE)
            while 1:
                self.device.sleep(0.5)
                self.device.screenshot()
                if self.appear(BUTTON_GG_SCRIPT_START_PROCESS, offset=(50, 50)):
                    self.device.click(BUTTON_GG_LUACHOOSE)
                    continue
                if not self.appear(BUTTON_GG_ENTER_PATH0, offset=(50, 50)) and self.appear(BUTTON_GG_BACK, offset=(50, 50)):
                    self.device.click(BUTTON_GG_BACK)
                    continue
                if self.appear(BUTTON_GG_ENTER_PATH0, offset=(50, 50)):
                    self.device.click(BUTTON_GG_BACK)
                    continue
                if self.appear(BUTTON_GG_ENTER_PATH1, offset=(50, 50)):
                    break

            skip_first_screenshot = True
            while 1:
                if skip_first_screenshot:
                    skip_first_screenshot = False
                else:
                    self.device.sleep(0.5)
                    self.device.screenshot()
                if self.appear_then_click(BUTTON_GG_PATH0, offset=(50, 50)):
                    continue
                if self.appear_then_click(BUTTON_GG_PATH1, offset=(50, 50)):
                    continue
                if self.appear_then_click(BUTTON_GG_LUA, offset=(50, 50)):
                    continue
                if self.appear(BUTTON_GG_SCRIPT_START_PROCESS, offset=(50, 50)):
                    break

    def gg_push(self):
        if self.oldpath == False:
            logger.hr('Push lua file')
            self.device.adb_push('bin/lua/Multiplier.lua', f"{self.luapath}")
            logger.info('Push success')
        else:
            logger.hr('Skip push lua file')

    def run(self, factor):
        self.factor = factor
        self.gg_push()
        self.gg_start()
        self.enter_gg()
        self.gg_enter_script()
        self.gg_mode()
        self.gg_handle_factor()
        self.gg_script_run()
        GGData(self.config).set_data(target='gg_on', value=True)
        self.skip_error()
        logger.attr('GG', 'Enabled')
        logger.hr('GG panel closed')
        self.gg_exit()