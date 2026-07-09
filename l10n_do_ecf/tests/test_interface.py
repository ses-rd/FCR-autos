# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged, Form
from .test_ecf_common import TestL10nDoEcfCommon
from unittest.mock import patch


@tagged('post_install_l10n', 'post_install', '-at_install')
class TestDoAccountMove(TestL10nDoEcfCommon):

    def Xtest_l10n_do_interface_test_connection(self):
        """"""
        self._setup_company_do_ecf()
        text_response = '{"token": "03a4a99c01db7a494e12fe4ba7f9af2995a63feco1737035156", "issued": "2024-01-17 13:45:56", "expired": "24-50-17 13:50:56"}'
        with patch('requests.post') as mock_post:
            Interface = self.env["ecf.settings"].with_company(self.company).sudo()
            ecf_setting = Interface.create({"name": "TEST",
                                            "user": "demo@netvux.com",
                                            "key": "d95f7d284f1a492915f4350feb3c4af17a55fb48",
                                            })

            mock_post.return_value.status_code = 200
            mock_post.return_value.text = text_response
            action_verify = ecf_setting.action_verify()
            loco1 = action_verify["params"]["message"]
            self.assertEqual(len(loco1), len(text_response))
