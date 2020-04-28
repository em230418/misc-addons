{
    "name": """S3 Attachment Storage""",
    "summary": """Upload attachments on Amazon S3""",
    "category": "Tools",
    "images": [],
    "version": "13.0.2.0.0",
    "application": False,
    "author": "IT-Projects LLC, Ildar Nasyrov",
    "website": "https://it-projects.info",
    "license": "Other OSI approved licence",  # MIT
    "price": 200.00,
    "currency": "EUR",
    "depends": [
        "base_setup",
        "product",  # Note: product dependency is for unittests only
    ],
    "external_dependencies": {"python": ["boto3"], "bin": []},
    "data": ["data/ir_attachment_s3_data.xml", "views/res_config_settings_views.xml"],
    "qweb": [],
    "demo": [],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "auto_install": False,
    "installable": True,
}
