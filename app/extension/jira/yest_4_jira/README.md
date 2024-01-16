### Plugin information
Yest4Jira introduces a new issue type named 'Yest Workflow'.
A Yest workflow is a graphical model to figure out some business rules.
A Yest workflow is designed by a tester or a PO and is comprehensive for all the stakeholders in a agile team.

**/!\   The concept of 'Yest Workflow' is not equivalent to the concept of workflow in Atlassian Jira. It's a graphical representation of testing use cases used in testing domain.**

The DataCenter/Server version of the app is available at :
https://jira.smartesting.com/yest4jira/yest4jira-server-3.0.0.obr

The content of the graphical representation is stored in a unique issue attachment named "workflow.yest".


###### Screenshots

1. Dedicated panel for 'Yest Workflow' issues. Dedicated issue type and dedicated attachment.

![](images/yestWorkflowIssue.png)

2. Yest Workflow Editor  
This editor is full client-side (React) and not uses a dedicated iframe (dialog displayed in fullscreen mode).  

![](images/yestWorkflowEditor.png)


### Testing Notes
* Yest4Jira add a new issue type in the Jira system: 'Yest Workflow'
* \>99% of the use of Yest4Jira consists in designing: create/modify a Jira ticket typed 'Yest Workflow'.  (first screenshot)
* \<1% of the use of Yest4Jira consists in importing existing diagrams (predefined Yest samples or local BPMN.iO files) (second screenshot)
* Depending on his attachment rights, a user may or may not modify a 'Yest Workflow' ticket.
* All modification actions are done via the Rest API.
* Yest4Jira does not add a new point in the existing API
* To create/update an issue with the type 'Yest Workflow' the issue project must refer the issue type 'Yest Workflow'. A Yest configuration page helps the user to associate this issue type with a project.
 For this Yest4Jira use the url "/plugins/servlet/yest/configuration" (POST request with json data = {project: 'your_project_key'})
 This request will be tested by a JMeter entry.


### How to implement
* The 'Yest Workflow' edition will be tested by a Selenium UI test case
* The 'Yest Workflow' import will be tested by a Selenium UI test case
* The project configuration for Yest (POST request) will be tested by a Jmeter test case

###### Selenium
Two test cases have been implemented according the 2 use cases (edition & import). These ones are in dedicated folder `app/extension/jira/yest_4_jira`.

* `app_yest4jira_import`: tests a Yest sample import from the 'Yest' page.
**This test must be commented if the app is not installed** (the 'Yest' page does not exist) 


* `app_yest4jira_edit`: tests the workflow edition & saving from any issue

    If the issue does not have the type 'Yest Workflow', then this type is selected among the available ones.
    
    If the current user does not have the permissions to create/delete the attachment, a warning message is expected.
    
    Else the test executes a workflow modification and save it through the dedicated editor.
     

###### JMeter
One test case has been implemented to test the POST request used to configure a project for Yest.
The frequency of project configuration is very low (set to 1%). **If the app is not installed this test must be disabled (set to 0%)**  

```
method: POST 
url: /plugins/servlet/yest/configuration
data: { project: '<your_project_key>' }
```


### Run test


Run test:
`bzt jira.yml`
