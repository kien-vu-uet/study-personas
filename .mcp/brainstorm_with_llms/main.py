import pathlib

from google import genai
from google.genai import types as genai_types
from openai import AsyncOpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from pydantic import BaseModel, Field, create_model

from fastmcp import FastMCP

mcp = FastMCP(
    name="Brainstorm-with-LLMs MCP",
    version="0.1.0",
)


@mcp.tool(
    name="brainstorm_with_openai_o3",
    title="Brainstorm with OpenAI O3",
    description="Book a consultation with OpenAI O3 to brainstorm ideas.",
    tags={"brainstorm"},
)
async def brainstorm_with_openai_o3(
    *,
    domain: str = "general",
    topic: str = "general",
    messages: list[ChatCompletionMessageParam],
    expected_output_schema: dict | None = Field(
        default=None,
        description="The output of the function `.model_json_schema()` from the expected output schema. It should be use to recover the schema in the client.",
    ),
    file_uri: str | None = Field(
        default=None,
        description="Optional local file URI of the mentioned documentation to be used in the understanding process.",
    ),
    # generation_config: dict = {},
) -> str:
    try:
        ExpectedOutputSchema = create_model(
            "ExpectedOutputSchema",
            **expected_output_schema,
        )
        assert issubclass(ExpectedOutputSchema, BaseModel), (
            "Expected output schema must be a subclass of BaseModel"
        )
    except Exception:
        ExpectedOutputSchema = None

    client = AsyncOpenAI()

    messages.insert(
        0,
        {
            "role": "system",
            "content": f"""You are an expert in the {domain} domain, focusing on the topic of {topic}.
Your task is to brainstorm ideas and provide insights based on the provided messages.
If there are any questions or requests for clarification, please ask your coworker(s) for more information or respond "Please clarify your request.""",
        },
    )

    if file_uri:
        # Retrieve and encode the PDF byte
        file_path = pathlib.Path(file_uri)

        # Upload the PDF using the File API
        uploaded_file = await client.files.create(
            file=file_path,
            purpose="user_data",
        )
        messages.append(
            {
                "role": "user",
                "content": {
                    "type": "file",
                    "file": {
                        "file_id": uploaded_file.id,
                    },
                },
            }
        )

    if not ExpectedOutputSchema:
        response = await client.chat.completions.create(
            model="o3",
            messages=messages,
            # **generation_config
        )
        return response.choices[0].message.content or "[No response provided]"
    else:
        response = await client.chat.completions.parse(
            model="o3",
            messages=messages,
            response_format=ExpectedOutputSchema,  # **generation_config
        )
        if not (parsed := response.choices[0].message.parsed):
            return response.choices[0].message.content or "[No response provided]"
        return parsed.model_dump_json(exclude_none=True, exclude_unset=True)


@mcp.tool(
    name="brainstorm_with_gemini_2_5_pro",
    title="Brainstorm with Gemini 2.5 Pro",
    description="Book a consultation with Gemini 2.5 Pro to brainstorm ideas.",
    tags={"brainstorm"},
)
async def brainstorm_with_gemini_2_5_pro(
    *,
    domain: str = "general",
    topic: str = "general",
    contents: genai_types.ContentListUnion | genai_types.ContentListUnionDict,
    file_uri: str | None = Field(
        default=None,
        description="Optional local file URI of the mentioned documentation to be used in the understanding process.",
    ),
) -> str:
    prompt = f"""You are an expert in the {domain} domain, focusing on the topic of {topic}.
Your task is to brainstorm ideas and provide insights based on the provided messages and the uploaded file (if exists).
If there are any questions or requests for clarification, please ask your coworker(s) for more information or respond "Please clarify your request."""

    contents = [prompt, *contents] if isinstance(contents, list) else [prompt, contents]

    client = genai.Client()

    if file_uri:
        # Retrieve and encode the PDF byte
        file_path = pathlib.Path(file_uri)

        # Upload the PDF using the File API
        uploaded_file = client.files.upload(
            file=file_path,
        )
        contents.append(uploaded_file)

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=contents,
    )
    return response.text or "[No response provided]"
