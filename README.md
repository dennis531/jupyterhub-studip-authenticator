# Jupyterhub Stud.IP Authenticator
The jupyterhub Stud.IP authenticator allows Jupyter notebooks to be integrated into Stud.IP as an LTI tool. Lecturers can use this tool in courses to provide students Jupyter notebooks. In contrast to lecturers, learners have read-only permissions to these notebooks, but are free to edit them. For each course, a separate workspace is created when it is called for the first time in a course. It based on the [LTI Launch JupyterHub Authenticator](https://github.com/jupyterhub/ltiauthenticator).

## Requirements
The authenticator only works with an installation of [The littlest JupyterHub](https://tljh.jupyter.org/).

## Installation
- Install and configure tljh (https://tljh.jupyter.org/en/latest/install/index.html)
- Clone this repository: `git clone https://github.com/virtUOS/jupyterhub-studip-authenticator.git`
- Navigate to cloned directory: `cd jupyterhub-studip-authenticator`
- Install this authenticator using pip: `sudo /opt/tljh/hub/bin/python -m pip install .`
- Change tljh configs:
  - `sudo tljh-config set auth.type studipauthenticator.StudipAuthenticator`
  - `sudo tljh-config set StudipAuthenticator.consumers {CONSUMER_KEY, CONSUMER_SECRET}`. Replace and configure `CONSUMER_KEY` and `CONSUMER_SECRET` as mentioned in https://github.com/jupyterhub/ltiauthenticator#the-consumers-setting-lti11authenticatorconsumers. Possibly you need to edit the file manually: `sudo vi /opt/tljh/config/config.yaml`, because the previous command sets unwanted quotation marks.
  - Check configurations: `sudo tljh-config show`
    - The configuration should contain similar information: 
        ```yaml
        auth:
        StudipAuthenticator:
          consumers: {123: 456}
        type: studipauthenticator.StudipAuthenticator
        ```
    - Restart the server: `sudo tljh-config reload`
- Configure Jupyter-LTI-Tool in Stud.IP: 
    - Admin (global): see https://hilfe.studip.de/admin/GlobalEinstellungen/LTI-Tools
    - User: see https://hilfe.studip.de/help/4.0/de/Basis/LTI-Tools
    - The Configurations are listed in the following [Configurations](#configurations) section
- Enjoy JupyterHub in Stud.IP!

## Configurations
- LTI-Tool-Configurations:
  - URL: `{your-juypterhub-url}/hub/lti/launch` (e.g. `https://jupyter.virtuos.uos.de/hub/lti/launch`)
  - Consumer-Key: `CONSUMER_KEY`
  - Consumer-Secret: `CONSUMER_SECRET`
  - OAuth Signature Method: `HMAC-SHA1`
  - Uncheck `Nutzendendaten an LTI-Tool senden`
  - More Details: https://hilfe.studip.de/help/4.0/de/Basis/LTI-Tools 


- Prevent new tabs in jupyter file browser (optional)
  - Create directory: `sudo mkdir -p /etc/skel/.jupyter/custom`
  - Create file `vi custom.js` with following content:
    ```javascript
    require(["base/js/namespace"], function (Jupyter) {
      Jupyter._target = '_self';
    });
    
    $(document).on("click", "a", function() {
      if ($(this).attr('target') == "_blank") {
          $(this).attr('target', '_self');
      }
    });
    ```
  - This function overrides the `target=_blank` attribute in `a` tags.

## Redirect automatically to specific Notebook
- Configure `Zusätzliche LTI-Parameter` in the Stud.IP LTI tool settings to redirect the jupyter user to a specific file (e.g. notebook): 
  - `next=/hub/user-redirect/tree/example/example_notebook.ipynb` 
  - or alternatively via `URL` configuration: `https://jupyter.virtuos.uos.de/hub/lti/launch?next=/hub/user-redirect/tree/example/example_notebook.ipynb`
  - In the value of the `next` parameter, `/example/example_notebook.ipynb` indicates the location of the file in the working directory.
- More details: 
  - https://jupyterhub.readthedocs.io/en/stable/getting-started/faq.html#how-do-i-share-links-to-notebooks
  - https://github.com/jupyterhub/ltiauthenticator#lti-11
  - Change user interface, see https://tljh.jupyter.org/en/latest/howto/env/notebook-interfaces.html#trying-an-alternate-interface-temporarily. 
    - For nteract interface replace `/tree` by `/nteract/tree`. 
    - **Note**: The modern jupyter lab interface doesn't work in redirects with LTI authentication.
