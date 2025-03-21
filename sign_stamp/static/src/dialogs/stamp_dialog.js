import { Dialog } from "@web/core/dialog/dialog";
import { SignNameAndSignature, SignNameAndSignatureDialog } from "@sign/dialogs/sign_name_and_signature_dialog";

export class LogoAndStamp extends SignNameAndSignature {
    static template = "sign_stamp.LogoAndStamp"; 
}

export class LogoAndStampDialog extends SignNameAndSignatureDialog {  
    static template = "sign_stamp.LogoAndStampDialog";
    static components = {
        Dialog,
        LogoAndStamp,
    };
}
