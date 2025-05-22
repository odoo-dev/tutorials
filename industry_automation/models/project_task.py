from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import zipfile
import os
import tempfile
import requests
import logging
import socket
import shutil
from markupsafe import Markup
from ..cleanup_scripts import script_old

# Setup logger
_logger = logging.getLogger(__name__)

 # Map DB version to fixed port
VERSION_PORT_MAP = {
    'saas~18.1': 10001,
    'saas~18.2': 10002,
}
BASE_URL = "http://localhost:"
PROJECT_NAME = "RD Fun Industry"
PROJECT_STAGE_NAME = "Spec"
MASTER_PASSWORD = "hyif-nir4-qjf5"
LOGIN = "admin"
PASSWORD = "admin"

class ProjectTask(models.Model):
    _inherit = 'project.task'

    module_name = fields.Char(string="Module Name", required=True)
    version = fields.Char(string="Dump Database Version", required=True)
    category = fields.Selection(
        selection=[
            ('services', 'Services'),
            ('retail', 'Retail'),
            ('construction', 'Construction'),
            ('hospitality', 'Hospitality'),
            ('health_and_fitness', 'Health and Fitness'),
            ('supply_chain', 'Supply Chain'),
        ],
        string="Module Category",
        required=True,
    )

    @api.model
    def process_all_new_tasks(self):
        # Step 1: Search for the project named 'RD Fun Industry' using sudo to bypass record rules
        project = self.env['project.project'].sudo().search([('name', '=', PROJECT_NAME)], limit=1)
        if not project:
            raise UserError("Project 'RD Fun Industry' not found.")
        project_id = project.id
        
        # Step 2: Locate the specific task stage within the project
        stage = self.env['project.task.type'].sudo().search([
                ('name', '=', PROJECT_STAGE_NAME),
                ('project_ids', 'in', int(project_id))
            ], limit=1)
        
        # Step 3: Find all tasks that are:
        #   - in the specified project
        #   - in the specified stage
        #   - currently in '01_in_progress' state
        tasks = self.env['project.task'].sudo().search([
            ('project_id', '=', int(project_id)),
            ('stage_id', '=', stage.id),
            ('state', '=', '01_in_progress'),
        ])

        # Step 4: Iterate through each matching task and call the custom 'process_task' method
        for task in tasks:
            task.process_task()

    def process_task(self):
        # Get all attachments linked to the current task
        attachments = self.attachment_ids
        
        for attachment in attachments:
            # Check if the attachment is a ZIP file AND contains '.dump' in its filename
            if attachment.name.lower().endswith('.zip') and '.dump' in attachment.name.lower():
                # Extract metadata from the task for export processing
                module_name = self.module_name
                version = self.version
                category = self.category

                # Call the method to export the zip file as a processed module  
                self.export_module_zip(attachment, module_name, version, category)

    def export_module_zip(self, attachment, module_name, version, category):
        try:
            # Extract industry name from the zip filename
            industry_name = attachment.name.split('.')[0]

            # 1. Download the attached dump file and store it temporarily
            temp_zip_file_path = self.download_dump_from_attachment(attachment)
            if not temp_zip_file_path:
                _logger.error("Failed to download dump file and store to temp")
                raise Exception("Failed to download dump file and store to temp")

            # 2. Get the DB version (first two parts of semantic versioning, e.g., 16.0)
            db_version = '.'.join(version.split('.')[:2])
            port = self.get_port_for_version(db_version)

            # Check if the appropriate Odoo server is running on the correct port
            if not self.is_port_open("localhost" , port):
                _logger.error(f"No server is running on port {port} for DB version {db_version}.")
                raise Exception(f"No server is running on port {port} for DB version {db_version}.")
            _logger.info(f"Server found on port {port} for DB version {db_version}.")

            # 3. Restore the DB using the dump file on the found port
            restore_db_name = f"{module_name}_db"
            success = self.restore_db(port, restore_db_name, temp_zip_file_path)
            if not success:
                _logger.error(f"Database '{restore_db_name}' Failed to restore  on port {port}.")
                raise Exception(f"Database '{restore_db_name}' Failed to restore  on port {port}.")
            _logger.info(f"Database '{restore_db_name}' restored successfully on port {port}.")

            # 4. Delete the temporary dump file
            self.delete_temp_file(temp_zip_file_path)

            # 5. Prepare a temporary base directory for exporting and modifying files
            base_temp_dir = os.path.join(tempfile.gettempdir(), industry_name)
            os.makedirs(base_temp_dir, exist_ok=True)

            # 6. Export the Studio customizations into a zip file
            studio_zip_path = f"{base_temp_dir}/studio_customization.zip"
            self.export_studio_customizations(port, restore_db_name, studio_zip_path)

            # 7. Extract the studio zip for cleaning up
            with zipfile.ZipFile(studio_zip_path, "r") as zip_ref:
                zip_ref.extractall(base_temp_dir)

            # 8. Run the external cleanup script to refactor the module
            studio_extract_path = f"{base_temp_dir}/studio_customization"
            # os.chdir(f"{base_temp_dir}")
            try:
                # script_path = "/home/odoo/odoo/industry/industry_automation/cleanup_scripts/script.py"
                # os.system(
                #     f"PYTHONPATH=/home/odoo/odoo/community python3 {script_path} "
                #     f"-d {restore_db_name} -m {module_name} -c {category} -p {studio_extract_path} --port {port}"
                # )
                script_old.main(module_name, category, restore_db_name, studio_extract_path, port, base_temp_dir)
                _logger.info("Module Clean Up successful")
            except Exception as e:
                raise Exception("Error while Running CleanUp Script")

            # 9. Convert both studio_customization and cleaned module folders back to zip files
            module_zip_path = self.compress_to_zip(module_name, base_temp_dir)
            studio_extract_zip_path = self.compress_to_zip("studio_customization", base_temp_dir)

            # 10. Upload both zips as Odoo attachments
            studio_extract_attachment = self.add_to_attachment(studio_extract_zip_path)
            module_attachment = self.add_to_attachment(module_zip_path)
            if not studio_extract_attachment:
                _logger.error("studio_customization.zip not upload on an attachment")
                raise Exception("studio_customization.zip not upload on an attachment")
            if not module_attachment:
                _logger.error(f"{module_name}.zip not upload on an attachment")
                raise Exception(f"{module_name}.zip not upload on an attachment")

            # 11. Cleanup temp directory after processing
            # self.delete_temp_dir(base_temp_dir)

            # 12. Update task state to "03_approved"
            self.sudo().write({'state': '03_approved'})

            # 13. Post a success message with attachments to the task chatter
            message = Markup(
                "<div style='color:green;'>"
                "✅ ZIP file <b>%s</b> processed successfully.<br/>"
                "✅ ZIP file <b>%s.zip</b> and <b>studio_customization.zip</b> uploaded successfully."
                "</div>"
            ) % (
                attachment.name,
                module_name,
            )
            self.message_post(
                body=message,
                attachment_ids=[studio_extract_attachment.id, module_attachment.id],
                message_type="notification",
                subtype_xmlid="mail.mt_comment",
            )
            self.drop_db(restore_db_name, port)
            _logger.info(f"studio_customization.zip and {module_name}.zip upload to task attachment successfully.")

        except Exception as e:
            # In case of any error, post a failure message to the task chatter
            message = Markup(
                "<div style='color:red;'>"
                "❌ Failed to process ZIP file <b>%s</b><br/><br/>"
                "%s."
                "</div>"
            ) % (
                attachment.name,
                str(e),
            )

            self.sudo().message_post(
                body=message,
                message_type="notification",
                subtype_xmlid="mail.mt_comment",
            )
  
    def download_dump_from_attachment(self, attachment):
        """
        Decodes the base64-encoded attachment content and writes it to a temporary .zip file.
        
        Args:
            attachment (ir.attachment): The attachment record containing a base64-encoded dump ZIP.

        Returns:
            str: Absolute file path to the saved temporary .zip file, or None if failed.
        """
        try:
            # Decode the base64-encoded file data to binary format
            file_data = base64.b64decode(attachment.datas)

            # Create a temporary file with .zip extension, without auto-deletion
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip', mode='wb') as temp_zip_file:
                # Write the binary file data to the temp file
                temp_zip_file.write(file_data)
                
                # Return the full file path of the written temp file
                return temp_zip_file.name

        except Exception as e:
            raise Exception("Failed to Download Dump DB file")

    def get_port_for_version(self, db_version):
        # Look up the port number mapped to the given DB version
        port = VERSION_PORT_MAP.get(db_version)

        # Raise an error if no port is found for the version
        if not port:
            _logger.error(f"No port mapped for DB version {db_version}")
            raise Exception(f"No port mapped for DB version {db_version}")
        return port
    
    def is_port_open(self, host: str, port: int, timeout: float = 1.0) -> bool:
        """Check if a TCP port is open on the given host."""
        
        # Create a TCP socket using IPv4
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Set the timeout for the connection attempt
            sock.settimeout(timeout)
            try:
                # Attempt to connect to the specified host and port
                sock.connect((host, port))
                return True
            except (socket.timeout, ConnectionRefusedError):
                # Return False if the connection times out or is refused
                return False

    def restore_db(self, port, db_name, temp_zip_file_path):
        """
        Restores the database from the given ZIP file to the Odoo server running on the specified port.

        Args:
            port (int): The port number of the Odoo server where the DB should be restored.
            db_name (str): The name to assign to the restored database.
            temp_zip_file_path (str): Path to the ZIP file containing the DB dump.

        Returns:
            bool: True if the database is restored and credentials are reset, False otherwise.
        """
        try:
            # Open the ZIP file containing the database dump
            with open(temp_zip_file_path, 'rb') as backup_file:
                # Send POST request to Odoo's database restore endpoint
                response = requests.post(
                    f'{BASE_URL}{port}/web/database/restore',
                    data={
                        'master_pwd': MASTER_PASSWORD,  # Master admin password
                        'name': db_name,                # Target DB name
                        'copy': True                    # Indicate it's a copy
                    },
                    files={
                        'backup_file': ('tattoo.zip', backup_file, 'application/zip')
                    }
                )

            # Check if the restore was successful (HTTP 200 OK or 302 Found)
            if response.status_code in (200, 302):
                # Reset login credentials for user ID 2
                os.system(f"psql {db_name} -c \"UPDATE res_users SET login='{LOGIN}', password='{PASSWORD}' WHERE id=2;\"")
                return True
            else:
                return False

        except Exception:
            raise Exception("Database Can't be Restore")

    def drop_db(self, db_name, port):
        response = requests.post(
            f'{BASE_URL}{port}/web/database/drop',
            data={
                'master_pwd': MASTER_PASSWORD,  # Master admin password
                'name': db_name,
            },
        )
        response.raise_for_status()

    def delete_temp_file(self, file_path):
        """
        Deletes a temporary ZIP file after use.
        
        :param zip_path: Full path to the ZIP file.
        """
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)

    def export_studio_customizations(self, port, db_name, studio_zip_path):
        try:
            session = requests.Session()
            # Step 1: Authenticate via /web/session/authenticate (sets session cookie)
            auth_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "db": db_name,
                    "login": LOGIN,
                    "password": PASSWORD,
                },
                "id": 1
            }
            response = session.post(f"{BASE_URL}{port}/web/session/authenticate", json=auth_payload)
            response.raise_for_status()

            # Parse login result
            result = response.json().get("result")
            if not result or not result.get("uid"):
                _logger.error("Authentication Failed")
                raise Exception("Login failed.")
            uid = result["uid"]
            _logger.info("Authentication Successful")
            
            # Step 2: Ensure web_studio is installed
            modules = self.check_web_studio_installed(port, db_name, uid)
            if modules:
                state = modules[0]['state']
                model_id = modules[0]['id']
                if state == "uninstalled":
                    self.install_web_studio(port, db_name, uid, model_id)
            else:
                _logger.error("web_studio module not found in registry.")
                raise Exception("web_studio module not found in registry.")

            # Step 3: Call action_preset on studio.export.model
            preset_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        db_name,
                        uid,
                        PASSWORD,
                        "studio.export.model",
                        "action_preset",
                        [{}],
                    ]
                },
                "id": 2
            }
            preset_resp = session.post(f"{BASE_URL}{port}/jsonrpc", json=preset_payload)
            preset_resp.raise_for_status()

            # Step 4: Create export wizard via RPC
            rpc_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                                db_name,
                                uid,
                                PASSWORD,
                                "studio.export.wizard",
                                "create",
                                [{
                                    "include_additional_data": True,
                                    "include_demo_data": True
                                }]
                            ]
                },
                "id": 3
            }

            wizard_resp = session.post(f"{BASE_URL}{port}/jsonrpc", json=rpc_payload)
            
            wizard_resp.raise_for_status()
            
            if not wizard_resp.json()["result"]:
                _logger.error("Export Wizard Failed to Create")
                raise Exception("wizard id not found")
            wizard_id = wizard_resp.json()["result"]

            # Step 5: Call the export route (no token needed, session is authenticated)
            export_url = f"{BASE_URL}{port}/web_studio/export?active_id={wizard_id}&token=dummytoken"
            export_resp = session.get(export_url, stream=True)
            

            if export_resp.status_code == 200 and export_resp.headers['Content-Type'] == 'application/zip':
                with open(studio_zip_path, "wb") as f:
                    f.write(export_resp.content)
            else:
                _logger.error(f" Export failed: {export_resp.status_code} - {export_resp.text}")
                raise Exception(f" Export failed: {export_resp.status_code} - {export_resp.text}")
            
        except Exception as e:
            _logger.error("studio_customization Failed to Export")
            raise Exception(str(e))

    def compress_to_zip(self, dir_name, parent_dir):
        # Construct the full path to the module directory
        dir_path = os.path.join(parent_dir, dir_name)
        # Define the path for the resulting ZIP file
        dir_zip_path = os.path.join(parent_dir, f"{dir_name}.zip")

        # Create a ZIP file and write all files from the module directory into it
        with zipfile.ZipFile(dir_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    # Store relative path to maintain directory structure inside ZIP
                    rel_path = os.path.relpath(full_path, dir_path)
                    zipf.write(full_path, arcname=rel_path)

        # Return the path to the created ZIP file
        return dir_zip_path
    
    def add_to_attachment(self, zip_path):
        try:
            # Open and read the ZIP file in binary mode
            with open(zip_path, "rb") as f:
                file_data = f.read()

            # Extract the file name from the full path
            file_name = zip_path.split('/')[-1]

            # Create an attachment record in Odoo with the ZIP content
            attachment = self.env['ir.attachment'].sudo().create({
                'name': file_name,
                'datas': base64.b64encode(file_data),
                'res_model': 'project.task',
                'res_id': self.id,
                'type': 'binary',
                'mimetype': 'application/zip',
            })

            # Return the created attachment record
            return attachment
        except Exception:
            return False

    def delete_temp_dir(self, dir_path):
        """
        Deletes a temporary directory and all its contents.
        
        :param dir_path: Full path to the directory.
        """
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            shutil.rmtree(dir_path)

    def check_web_studio_installed(self, port, db_name, uid):
        # Prepare the JSON-RPC payload to search for the 'web_studio' module
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    db_name, uid, PASSWORD,
                    "ir.module.module", "search_read",
                    [[["name", "=", "web_studio"]]],
                    {"fields": ["state"], "limit": 1}
                ]
            },
            "id": 2
        }

        # Send the request to the server and parse the JSON response
        response = requests.post(f"{BASE_URL}{port}/jsonrpc", json=payload).json()
        
        # Return the list of matched module(s) with their state
        if response["result"]:
            return response["result"]

    def install_web_studio(self, port, db_name, uid, module_id):
        # Prepare JSON-RPC payload to install the module using button_immediate_install
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    db_name, uid, PASSWORD,
                    "ir.module.module", "button_immediate_install",
                    [module_id]
                ]
            },
            "id": 4
        }

        # Send request to install the module
        install_response = requests.post(f"{BASE_URL}{port}/jsonrpc", json=payload).json()

        # Log error if installation failed
        if not install_response["result"]:
            _logger.error("Module Studio can't install")
        return install_response["result"]




    

    
    


    
