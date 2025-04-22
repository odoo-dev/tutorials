/** @odoo-module */

import { getFixture } from "@web/../tests/helpers/utils";
import { makeTestEnv } from "@web/../tests/helpers/mock_env";
import {
    makeFakeDialogService,
    makeFakeLocalizationService,
    patchUserWithCleanup,
} from "@web/../tests/helpers/mock_services";
import { StampDialog } from "@sign_stamp/dialogs/stamp_dialog";
import { registry } from "@web/core/registry";
import { hotkeyService } from "@web/core/hotkeys/hotkey_service";
import { uiService } from "@web/core/ui/ui_service";
import { popoverService } from "@web/core/popover/popover_service";
import { mountInFixture } from "@web/../tests/helpers/mount_in_fixture";

const serviceRegistry = registry.category("services");

let target;
const name = "Brandon Freeman";
const company = "MyCompany Pvt Ltd";
const address = "Infocity";
const city = "Ghandhinagar";
const country = "India";
const vat = "123456";
const logo = "";
const hash = "abcdef..."

QUnit.module("Stamp Dialog", function (hooks) {
    const mountStampDialog = async () => {
        const mockRPC = async (route) => {
            if(route.includes("/web/sign/get_fonts/")) {
                return {}
            }
        };
        const env = await makeTestEnv({ mockRPC });
        env.dialogData = {
            isActive: true,
            close: () => {}
        };
        await mountInFixture(StampDialog, target, {
            props: {
                signature: {
                    name,
                    company,
                    address,
                    city,
                    country,
                    vat,
                    logo,
                },
                frame: {},
                signatureType: "stamp",
                displaySignatureRatio: 1,
                activeFrame: true,
                defaultFrame: "",
                mode: "auto",
                hash,
                onConfirm: () => {},
                onConfirmAll: () => {},
                onCancel: () => {},
                close: () => {},
            },
            env,
        });
    };

    hooks.beforeEach(() => {
            target = getFixture();
            serviceRegistry.add("dialog", makeFakeDialogService());
            serviceRegistry.add("localization", makeFakeLocalizationService());
            serviceRegistry.add("ui", uiService);
            serviceRegistry.add("hotkey", hotkeyService);
            serviceRegistry.add("popover", popoverService);
        });

    QUnit.test("stamp dialog renders correctly", async function (assert) {
        const hasGroup = async () => true;
        patchUserWithCleanup({ hasGroup });

        await mountStampDialog();

        assert.deepEqual(
            [...target.querySelectorAll(".btn-primary, .btn-secondary")].map(
                (el) => el.textContent
            ),
            ["Upload", "Sign all", "Sign", "Cancel"],
            "should show buttons"
        );
        assert.strictEqual(
            target.querySelector('input[name="signer"]').value,
            name,
            "Should auto-fill the name"
        );
        assert.containsOnce(target, ".form-check", "should show frame in dialog");
        assert.notOk(
            target.querySelector(".form-check").classList.contains("d-none"),
            "frame should be shown"
        );
        assert.containsOnce(target, ".o_sign_frame.active");
        assert.strictEqual(
            target.querySelector(".o_sign_frame.active p").getAttribute("hash"),
            hash,
            "hash should be in the signature dialog"
        );
    });

    QUnit.test(
        "stamp dialog - frame is hidden when user is not from the sign user group",
        async (assert) => {
            await mountStampDialog();

            assert.ok(
                target.querySelector(".form-check").classList.contains("d-none"),
                "frame should be hidden"
            );
        }
    );

})
