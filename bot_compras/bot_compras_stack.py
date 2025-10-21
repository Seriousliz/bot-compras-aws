from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_cognito as cognito,
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_iam as iam,
    aws_logs as logs,
    CfnOutput
)
from constructs import Construct

class BotComprasStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Cognito User Pool
        user_pool = cognito.UserPool(self, "BotUserPool",
            user_pool_name="bot-compras-users",
            sign_in_aliases=cognito.SignInAliases(email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        # Cognito User Pool Client
        user_pool_client = cognito.UserPoolClient(self, "BotUserPoolClient",
            user_pool=user_pool,
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
                admin_user_password=True  # Habilitar ADMIN_NO_SRP_AUTH
            ),
            generate_secret=False
        )

        # S3 Bucket para audio
        audio_bucket = s3.Bucket(self, "AudioBucket",
            versioned=False,
            encryption=s3.BucketEncryption.S3_MANAGED,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteAfter90Days",
                    expiration=Duration.days(90),
                    enabled=True
                )
            ],
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.PUT],
                    allowed_origins=["*"],
                    allowed_headers=["*"]
                )
            ],
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # DynamoDB para historial
        conversations_table = dynamodb.Table(self, "ConversationsTable",
            table_name="conversaciones",
            partition_key=dynamodb.Attribute(
                name="user_email",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # IAM Role para Lambdas
        lambda_role = iam.Role(self, "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        # Permisos adicionales para Lambdas
        lambda_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "bedrock:InvokeModel",
                "transcribe:StartTranscriptionJob",
                "transcribe:GetTranscriptionJob",
                "polly:SynthesizeSpeech",
                "lex:RecognizeText",
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:Query",
                "s3:GetObject",
                "s3:PutObject"
            ],
            resources=["*"]
        ))

        # Lambda principal del bot
        bot_lambda = _lambda.Function(self, "BotLambda",
            function_name="bot-main",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="index.lambda_handler",  # Cambiar handler para código inline
            code=_lambda.Code.from_inline(f"""
import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    try:
        # Parsear el cuerpo de la solicitud
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
            
        mensaje = body.get('message', '')
        user_email = body.get('user_email', 'unknown')
        audio_data = body.get('audio_data')
        
        # 1. Clasificar intención (simulado)
        intencion = 'soporte' if any(word in mensaje.lower() for word in ['problema', 'error', 'falla', 'roto', 'soporte']) else 'compra'
        
        if intencion == 'soporte':
            respuesta = "Este canal es solo para asistencia de compras. Para soporte técnico, contacte nuestro departamento especializado."
            productos = []
            audio_url = None
        else:
            # 2. Procesar mensaje (simulado)
            if audio_data:
                # En producción usar Transcribe
                mensaje_procesado = "Quiero comprar electrodomésticos"
            else:
                mensaje_procesado = mensaje
            
            # 3. Generar respuesta (simulado - en producción usar Bedrock)
            respuesta = "¡Hola! Te ayudo a encontrar el electrodoméstico perfecto. Para recomendarte mejor, ¿podrías decirme qué tipo de electrodoméstico buscas y cuál es tu presupuesto aproximado?"
            
            # 4. Consultar productos (simulado)
            productos = [
                {{
                    "nombre": "Refrigerador Samsung RF28T5001SR",
                    "costo": 1299.99,
                    "url_producto": "https://tienda.com/productos/refrigerador-samsung-rf28t5001sr",
                    "descripcion": "Refrigerador de 28 pies cúbicos con tecnología Twin Cooling Plus"
                }},
                {{
                    "nombre": "Lavadora LG WM3900HWA", 
                    "costo": 899.99,
                    "url_producto": "https://tienda.com/productos/lavadora-lg-wm3900hwa",
                    "descripcion": "Lavadora de carga frontal 4.5 cu ft con TurboWash"
                }}
            ]
            
            # 5. Guardar en DynamoDB
            try:
                dynamodb = boto3.resource('dynamodb')
                table = dynamodb.Table('{conversations_table.table_name}')
                table.put_item(
                    Item={{
                        'user_email': user_email,
                        'timestamp': datetime.now().isoformat(),
                        'mensaje': mensaje_procesado,
                        'respuesta': respuesta,
                        'productos_mostrados': json.dumps(productos)
                    }}
                )
            except Exception as e:
                print(f"Error guardando en DynamoDB: {{e}}")
            
            # 6. Generar audio si es necesario
            audio_url = None
            if audio_data:
                try:
                    polly_client = boto3.client('polly')
                    s3_client = boto3.client('s3')
                    
                    response = polly_client.synthesize_speech(
                        Text=respuesta,
                        OutputFormat='mp3',
                        VoiceId='Lucia',
                        LanguageCode='es-ES'
                    )
                    
                    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
                    key = f"audio/{{user_email}}/{{timestamp_str}}.mp3"
                    
                    s3_client.put_object(
                        Bucket='{audio_bucket.bucket_name}',
                        Key=key,
                        Body=response['AudioStream'].read(),
                        ContentType='audio/mpeg'
                    )
                    
                    audio_url = f"https://{audio_bucket.bucket_name}.s3.amazonaws.com/{{key}}"
                    
                except Exception as e:
                    print(f"Error generando audio: {{e}}")
        
        # Respuesta final
        response_body = {{
            'respuesta': respuesta,
            'productos': productos,
            'audio_url': audio_url,
            'intencion': intencion
        }}
        
        return {{
            'statusCode': 200,
            'headers': {{
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS',
                'Content-Type': 'application/json'
            }},
            'body': json.dumps(response_body)
        }}
        
    except Exception as e:
        print(f"Error general: {{e}}")
        return {{
            'statusCode': 500,
            'headers': {{
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            }},
            'body': json.dumps({{'error': str(e)}})
        }}
            """),
            timeout=Duration.seconds(30),
            memory_size=512,
            role=lambda_role,
            environment={
                'S3_BUCKET': audio_bucket.bucket_name,
                'DYNAMODB_TABLE': conversations_table.table_name
            }
        )

        # Permisos para acceder a recursos
        audio_bucket.grant_read_write(bot_lambda)
        conversations_table.grant_read_write_data(bot_lambda)

        # API Gateway
        api = apigateway.RestApi(self, "BotAPI",
            rest_api_name="ChatAPI",
            description="API para bot de asistencia de compras",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"]
            )
        )

        # Endpoints de API
        chat_resource = api.root.add_resource("chat")
        chat_resource.add_method("POST", 
            apigateway.LambdaIntegration(bot_lambda)
            # Temporalmente sin autenticación para pruebas
        )

        health_resource = api.root.add_resource("health")
        health_resource.add_method("GET",
            apigateway.MockIntegration(
                integration_responses=[
                    apigateway.IntegrationResponse(
                        status_code="200",
                        response_templates={
                            "application/json": '{"status": "OK", "timestamp": "$context.requestTime"}'
                        }
                    )
                ],
                request_templates={
                    "application/json": '{"statusCode": 200}'
                }
            ),
            method_responses=[
                apigateway.MethodResponse(status_code="200")
            ]
        )

        # Outputs
        CfnOutput(self, "UserPoolId", 
            value=user_pool.user_pool_id,
            description="ID del User Pool de Cognito"
        )
        CfnOutput(self, "UserPoolClientId", 
            value=user_pool_client.user_pool_client_id,
            description="ID del Client del User Pool"
        )
        CfnOutput(self, "APIEndpoint", 
            value=api.url,
            description="URL del API Gateway"
        )
        CfnOutput(self, "AudioBucketName", 
            value=audio_bucket.bucket_name,
            description="Nombre del bucket S3 para audio"
        )
        CfnOutput(self, "ConversationsTableName", 
            value=conversations_table.table_name,
            description="Nombre de la tabla DynamoDB"
        )
