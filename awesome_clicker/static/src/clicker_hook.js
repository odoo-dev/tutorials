import { useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export function useClicker() {
  const clicker = useState(useService("clicker"));
  return clicker;
}
