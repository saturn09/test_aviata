from enum import Enum

TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIzMWM1ZDZmNy03NGJh" \
        "LTRmZGUtOGYyMS1kN2JhNDE4YTI3MWMiLCJpc3MiOiJ2RjJmMUNtSHlzYmRGdmJkR" \
        "1ZVdE5BNkd3WGplOWhKeiIsImlhdCI6MTU0Mjg4MzA0NSwiZXhwIjoyODY3Mzk1MD" \
        "Q1LCJjb25zdW1lciI6eyJpZCI6ImQ5YjNlNzlmLTQ4YTYtNDM3ZC05MDViLTk3NzQ" \
        "4ZWVmMDVlZCIsIm5hbWUiOiJjaG9jby1rei5ob3N0In19.oAcPmer0vsnSZeKUmMv" \
        "Pj0emnQopIQKWcaPg7-_cQgA"


class Route(Enum):
    ALA_TSE = 'ALA-TSE'
    TSE_ALA = 'TSE-ALA'
    ALA_MOW = 'ALA-MOW'
    MOW_ALA = 'MOW-ALA'
    ALA_CIT = 'ALA-CIT'
    CIT_ALA = 'CIT-ALA'
    TSE_MOW = 'TSE-MOW'
    MOW_TSE = 'MOW-TSE'
    TSE_LED = 'TSE-LED'
    LED_TSE = 'LED-TSE'
