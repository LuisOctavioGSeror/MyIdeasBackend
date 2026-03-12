from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.core.config import get_settings
from app.schemas.chat import ChatIn, ChatOut
from app.infrastructure.llm.provider_factory import get_llm_client
from app.services.chat_service import ChatService
from app.controllers.auth import get_current_user, oauth2_scheme
from app.schemas.auth import CurrentUserToken

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatOut, summary="Chat (JWT Bearer)")
async def chat(
    in_: ChatIn,
    current: CurrentUserToken = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
):
    s = get_settings()
    try:
        llm = get_llm_client(in_.provider, in_.model)
        service = ChatService(llm, s.mcp_url)
        answer = await service.run([m.model_dump() for m in in_.messages], token=token)
        prov = in_.provider or s.llm_provider
        model = in_.model or (s.openai_model if prov == "openai" else s.anthropic_model)
        return ChatOut(provider=prov, model=model, answer=answer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/stream", summary="Chat streaming (JWT Bearer)")
async def chat_stream(
    in_: ChatIn,
    current: CurrentUserToken = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
):
    """
    Endpoint que faz streaming real da resposta do LLM via SSE.
    """
    s = get_settings()

    try:
        llm = get_llm_client(in_.provider, in_.model)
        service = ChatService(llm, s.mcp_url)
        msgs = [m.model_dump() for m in in_.messages]

        async def event_generator():
            try:
                async for chunk in service.stream(msgs, token=token):
                    # SSE: cada pedaço vai em um evento "data"
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                # Erro no fluxo também vai como evento separado
                yield f"event: error\ndata: {str(e)}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))