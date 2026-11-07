from sms_ir import SmsIr

sms_ir = SmsIr(
    'gRpKugNF4Oqso8S7BCJR13GbDMiC98ZBBD6bEVhkvpQCHzWw1jIUK1xu78YVW4oV',
    '3000882868',
)


def sms_verification_code(number, code):
    sms_ir.send_verify_code(
        number=str(number),
        template_id=797820,
        parameters=[
            {
                "name": "code",
                "value": str(code),
            },
        ],
    )


def smsToMany(numbers, message):
    sms_ir.send_bulk_sms(
        numbers,
        message,
    )
