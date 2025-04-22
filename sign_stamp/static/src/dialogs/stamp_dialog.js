import { Dialog } from "@web/core/dialog/dialog";
import { SignNameAndSignature, SignNameAndSignatureDialog } from "@sign/dialogs/sign_name_and_signature_dialog";

export class Stamp extends SignNameAndSignature{
    static template = "sign_stamp.Stamp";

    triggerFileUpload(){
        const fileInput = document.querySelector("input[name='logo']");
        if (fileInput){
            fileInput.click();
        }
        else{
            console.log("File input not found");
        }
    }
}

export class StampDialog extends SignNameAndSignatureDialog {
    static template = "sign_stamp.StampDialog";

    static components = { Dialog, Stamp };

    get dialogProps(){
        return{
            title: "Adopt Your Stamp", size: "md",
        }
    }
}
