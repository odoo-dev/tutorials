import { LogoAndStampDialog } from "../../dialogs/stamp_dialog";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";
import { SignablePDFIframe } from "@sign/components/sign_request/signable_PDF_iframe";
import { SignNameAndSignatureDialog } from "@sign/dialogs/dialogs";
import { user } from "@web/core/user";

patch(SignablePDFIframe.prototype, {
    enableCustom(signItem) {
        super.enableCustom(signItem);
        const { el: signItemElement, data: signItemData } = signItem;
        const signItemType = this.signItemTypesById[signItemData.type_id];
        const { item_type: type } = signItemType;

        if (type === "stamp") {
            signItemElement.addEventListener("click", (e) => {
                this.handleSignatureDialogClick(e.currentTarget, signItemType);
            });
        }
    },

    openSignatureDialog(signatureItem, type) {
        if (this.dialogOpen) return;

        const DialogComponent = type.item_type === "stamp" ? LogoAndStampDialog : SignNameAndSignatureDialog;

        this.closeFn = this.dialog.add(
            DialogComponent,
            this.getDialogData(signatureItem, type),
            {
                onClose: () => {
                    this.dialogOpen = false;
                },
            }
        );
    },

    getDialogData(signatureItem, type) {
        const signature = {
            name: this.props.signerName,
            company: this.props.company,
            address: this.props.address,
            city: this.props.city,
            country: this.props.country,
            vat: this.props.vat,
            logo: this.props.logo,
        };
        const frame = {};
        const { height, width } = signatureItem.getBoundingClientRect();
        const signFrame = signatureItem.querySelector(".o_sign_frame");
        const signMode = type.auto_value ? "draw" : "auto"
        const signatureImage = signatureItem?.dataset?.signature;
        if (signatureImage) {
            signature.signatureImage = signatureImage;
        }
        return { //returns necessary data to feed into dialog and also defines what happens when clicking sign sign all and cancel
            frame,
            signature,
            signatureType: type.item_type,
            displaySignatureRatio: width / height,
            activeFrame: Boolean(signFrame) || !type.auto_value,
            mode: signMode,
            defaultFrame: type.frame_value || "",
            hash: this.frameHash,
            signatureImage,
            onConfirm: async () => {
                if (!signature.isSignatureEmpty && signature.signatureChanged) {
                    this.signerName = signature.name;
                    await frame.updateFrame();
                    const frameData = frame.getFrameImageSrc();
                    const signatureSrc = signature.getSignatureImage();
                    type.auto_value = signatureSrc;
                    type.frame_value = frameData;
                    if (user.userId) {
                        await this.updateUserSignature(type);
                    }
                    this.fillItemWithSignature(signatureItem, signatureSrc, {
                        frame: frameData,
                        hash: this.frameHash,
                    });
                } else if (signature.signatureChanged) {
                    delete signatureItem.dataset.signature;
                    delete signatureItem.dataset.frame;
                    signatureItem.replaceChildren();
                    const signHelperSpan = document.createElement("span");
                    signHelperSpan.classList.add("o_sign_helper");
                    signatureItem.append(signHelperSpan);
                    if (type.placeholder) {
                        const placeholderSpan = document.createElement("span");
                        placeholderSpan.classList.add("o_placeholder");
                        placeholderSpan.innerText = type.placeholder;
                        signatureItem.append(placeholderSpan);
                    }
                }
                this.closeDialog();
                this.handleInput();
            },

            onConfirmAll: async () => {
                this.signerName = signature.name;
                await frame.updateFrame();
                const frameData = frame.getFrameImageSrc();
                const signatureSrc = signature.getSignatureImage();
                type.auto_value = signatureSrc;
                type.frame_value = frameData;
                if (user.userId) {
                    await this.updateUserSignature(type);
                }
                for (const page in this.signItems) {
                    const promises = Object.values(this.signItems[page]).reduce((list, signItem) => {
                        const isSameType =
                            signItem.data.responsible === this.currentRole &&
                            signItem.data.type_id === type.id;

                        if (isSameType) {
                            list.push(
                                Promise.all([
                                    this.adjustSignatureSize(signatureSrc, signItem.el),
                                    this.adjustSignatureSize(frameData, signItem.el),
                                ]).then(([data, adjustedFrame]) => {
                                    this.fillItemWithSignature(signItem.el, data, {
                                        frame: adjustedFrame,
                                        hash: this.frameHash,
                                    });
                                })
                            );
                        }

                        return list;
                    }, []);

                    await Promise.all(promises);
                }

                this.closeDialog();
                this.handleInput();
            },

            onCancel: () => {
                this.closeDialog();
            },
        };
    },

    async updateUserSignature(type) {
        return  await rpc("/sign/update_user_signature", {
            sign_request_id: this.props.requestID,
            role: this.currentRole,
            signature_type: type.item_type === "signature" ? "sign_signature" : 
                            type.item_type === "stamp" ? "sign_stamp" : 
                            "sign_initials",
            datas: type.auto_value,
            frame_datas: type.frame_value,
        });
    },

    getSignatureValueFromElement(item) {
        if(item.data.type === "stamp"){
            return item.el.dataset.signature;
        }
        else{
            return super.getSignatureValueFromElement(item);
        }
    }
});
