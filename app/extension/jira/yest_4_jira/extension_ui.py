from lib2to3.pgen2 import driver
import random
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium_ui.jira.pages.selectors import IssueLocators
from selenium_ui.jira.pages.pages import Issue
from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from util.conf import JIRA_SETTINGS
from selenium import webdriver


class ImportLocators:
    menu_import = (By.ID, "yest-btn-main-import")
    tile_sample = (By.ID, "yest-tile-import-sample")
    select_project = (By.ID, "yest-import-select-project")
    select_options = (By.CLASS_NAME, "react-select__option")
    btn_import = (By.ID, 'yest-btn-import-doImport')
    btn_terminate = (By.ID, 'yest-btn-import-sample-terminate')
    tile_sample_LR = (By.ID, 'yest-tile-sample-LR')


class WorkflowIssueLocators:
    field_issuetype = (By.ID, "type-val")
    input_issuetype = (By.ID, 'issuetype-field')
    issuetype_suggestions = (By.ID, 'issuetype-suggestions')
    issuetype_options = (By.CLASS_NAME, "aui-list-item")
    issuetype_submit = (By.CLASS_NAME, 'submit')
    workflow_webpanel = (By.ID, "yest4jira-workflow-issue-web-panel")
    btn_edit = (By.ID, "yest-btn-open-workflow-editor")
    palette_btn_task = (By.ID, "yest-workflow-editor-palette-task")
    palette_btn_start = (By.ID, "yest-workflow-editor-palette-start")
    btn_close = (By.ID, 'yest-btn-close-workflow-editor')
    btn_save_close = (By.ID, "yest-btn-save-close")
    message_wrong_permissions = (By.ID, "yest-warning-insufficient-rights")


def import_button_is_enabled(page):
    import_button = page.get_element(ImportLocators.btn_import)
    return import_button.is_enabled() and import_button.text == "Import"

def import_sample(webdriver, page, sample_tile_locator):
    page.wait_until_clickable(ImportLocators.tile_sample).click()
    # Select random project until selection is configured for Yest
    is_yest_project = False
    attempts = 10
    while not is_yest_project and attempts >= 0:
        attempts -= 1
        page.wait_until_clickable(ImportLocators.select_project).click()
        project_list = page.get_elements(ImportLocators.select_options)
        if not project_list:
            return False
        rnd_project_el = random.choice(project_list)
        page.action_chains().move_to_element(rnd_project_el).click(rnd_project_el).perform()
        try:
            WebDriverWait(webdriver, 1.5).until(lambda wd: import_button_is_enabled(page))
            is_yest_project = True
        except TimeoutException:
            is_yest_project = False
    if not is_yest_project:
        return False
    page.get_element(sample_tile_locator).click()  # Click sample
    page.get_element(ImportLocators.btn_import).click()  # Click 'import'
    page.wait_until_clickable(ImportLocators.btn_terminate).click()  # Click button 'Terminate'
    return True


def app_yest4jira_import(webdriver, datasets):
    page = BasePage(webdriver)

    @print_timing("selenium_yest4jira_import:import_LR_sample")
    def import_LR_sample():
        page.go_to_url(f"{JIRA_SETTINGS.server_url}/plugins/servlet/yest/mainPage")
        webdriver.switch_to.frame("yest-main-page-iframe")
        page.wait_until_clickable(ImportLocators.menu_import).click()  # Wait for import button
        imported = import_sample(webdriver, page, ImportLocators.tile_sample_LR)  # import sample Leave Request
        webdriver.switch_to.default_content()
        return imported

    @print_timing("selenium_yest4jira_import:check_created_issue")
    def check_created_issue():
        issue_page = Issue(webdriver)
        issue_page.wait_for_issue_title()
        assert page.get_element(IssueLocators.issue_title).text == 'Leave Requests'

    if import_LR_sample():
        check_created_issue()


def is_yest_workflow_type(element):
    return "yest-workflow" in element.get_attribute("class").lower()


def set_yest_workflow_issue_type(webdriver, issue_page):
    field = issue_page.wait_until_visible(WorkflowIssueLocators.field_issuetype)
    if field.text == 'Yest Workflow':
        return True
    elif not "editable-field" in field.get_attribute("class"):
        return False
    else:
        field.click()
        issue_page.wait_until_clickable(WorkflowIssueLocators.input_issuetype).click()
        issue_page.wait_until_visible(WorkflowIssueLocators.issuetype_suggestions)
        issue_types = issue_page.get_elements(WorkflowIssueLocators.issuetype_options)

        filtered_issue_elements = list(filter(is_yest_workflow_type, issue_types))
        if filtered_issue_elements:
            rnd_issue_type_el = random.choice(filtered_issue_elements)
            issue_page.action_chains().move_to_element(rnd_issue_type_el).click(rnd_issue_type_el).perform()
            issue_page.wait_until_clickable(WorkflowIssueLocators.issuetype_submit).click()
            issue_page.wait_until_visible(WorkflowIssueLocators.workflow_webpanel)
            webdriver.switch_to.frame("yest-workflow-panel-iframe")
            issue_page.wait_until_visible(WorkflowIssueLocators.btn_edit)
            webdriver.switch_to.default_content()
            return True
        else:
            return False


def app_yest4jira_edit(webdriver, datasets):
    page = BasePage(webdriver)
    issue_key = datasets['current_session']['issue_key']
    page.go_to_url(f"{JIRA_SETTINGS.server_url}/browse/{issue_key}")
    page.wait_until_visible((By.CSS_SELECTOR, '.aui-navgroup-vertical>.aui-navgroup-inner')) # Wait for repo navigation panel is visible

    @print_timing("selenium_yest4jira:edit_workflow")
    def edit_workflow():
        # add task in workflow
        btn_task = page.wait_until_visible(WorkflowIssueLocators.palette_btn_task) # Wait for palette/task button
        btn_task.click()  
        action = ActionChains(webdriver)
        action.move_to_element_with_offset(btn_task, 200, 0)
        action.click()
        action.perform()
        # save and close
        page.get_element(WorkflowIssueLocators.btn_close).click()  # close
        page.wait_until_clickable(WorkflowIssueLocators.btn_save_close).click()  # Wait for 'save and close' button
        page.wait_until_invisible(WorkflowIssueLocators.btn_close)  # Wait for close button disappears

    installed = set_yest_workflow_issue_type(webdriver, page)
    if installed:
        webdriver.switch_to.frame("yest-workflow-panel-iframe")
        edit_button = page.wait_until_visible(WorkflowIssueLocators.btn_edit)
        if edit_button.is_enabled():
            edit_button.click()
            webdriver.switch_to.default_content()
            webdriver.switch_to.frame("workflow-editor-dialog-iframe")
            edit_workflow()
        else:
            page.wait_until_visible(WorkflowIssueLocators.message_wrong_permissions)
        webdriver.switch_to.default_content()
