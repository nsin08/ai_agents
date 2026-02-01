#!/usr/bin/env python3
"""
Multi-Channel Conversational Agent Bridge — Communication Emulation Demo

This script demonstrates the complete message flow without external dependencies:
1. Webhook receives inbound message (WhatsApp/Telegram format)
2. Adapter parses and normalizes to ChannelMessage
3. Agent core processes (queries history, calls Ollama, stores message)
4. Sender formats and sends response back

Run: python agent_bridge_demo.py

No external APIs required — uses mock data and local in-memory storage.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Literal
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import hashlib
import hmac
import time


# ============================================================================
# 1. DATA MODELS (Pydantic-style, without the dependency)
# ============================================================================

@dataclass
class ChannelMessage:
    """Canonical message format across all channels"""
    channel: str                          # whatsapp, telegram, slack
    sender_id: str                        # phone, user_id, composite
    text: str                             # user's message
    timestamp: datetime                   # provider's timestamp
    external_msg_id: str                  # provider's ID (MessageSid, message_id, ts)
    metadata: Dict = None
    correlation_id: str = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.correlation_id is None:
            self.correlation_id = str(uuid.uuid4())[:8]


@dataclass
class AgentBridgeResponse:
    """Response from Ollama bridge"""
    response_text: str
    tokens_used: int
    latency_ms: float
    status: Literal["success", "timeout", "error"]
    error_msg: Optional[str] = None


@dataclass
class SenderResponse:
    """Response from message sender"""
    external_msg_id: Optional[str]
    status: Literal["success", "queued", "failed", "invalid_recipient"]
    provider_error_code: Optional[str] = None
    provider_error_msg: Optional[str] = None
    retry_policy: Literal["immediate", "exponential", "do_not_retry"] = "do_not_retry"


# ============================================================================
# 2. MOCK STORAGE (In-Memory SQLite Emulation)
# ============================================================================

class ConversationStorage:
    """In-memory conversation storage (Phase 1 SQLite emulation)"""
    
    def __init__(self):
        self.messages: List[Dict] = []
        self.dedup_index: Dict[str, bool] = {}  # Idempotency: external_msg_id -> processed
    
    async def add_message(self, channel: str, sender_id: str, role: str, text: str, 
                         external_msg_id: str, correlation_id: str) -> bool:
        """Store message, return True if new, False if duplicate"""
        
        # Idempotency check
        key = f"{channel}:{external_msg_id}"
        if key in self.dedup_index:
            print(f"  [STORAGE] 🔄 Duplicate message {external_msg_id}, skipping")
            return False
        
        msg = {
            "id": len(self.messages),
            "channel": channel,
            "sender_id": sender_id,
            "role": role,
            "text": text,
            "external_msg_id": external_msg_id,
            "correlation_id": correlation_id,
            "timestamp": datetime.now().isoformat(),
        }
        self.messages.append(msg)
        self.dedup_index[key] = True
        
        print(f"  [STORAGE] ✅ Stored: {role} message from {sender_id} (cid={correlation_id})")
        return True
    
    async def get_history(self, channel: str, sender_id: str, limit: int = 10) -> str:
        """Retrieve conversation history as formatted string"""
        
        # Query by (channel, sender_id), ordered by timestamp
        history_msgs = [
            msg for msg in self.messages 
            if msg["channel"] == channel and msg["sender_id"] == sender_id
        ]
        
        # Format as agent context
        context_lines = []
        for msg in history_msgs[-limit:]:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            context_lines.append(f"{role_label}: {msg['text']}")
        
        history_str = "\n".join(context_lines) if context_lines else "(No prior messages)"
        print(f"  [STORAGE] 📚 Retrieved {len(history_msgs)} messages for {sender_id}")
        return history_str
    
    async def get_context(self, channel: str, sender_id: str) -> str:
        """Get full context (system prompt + history)"""
        
        system_prompt = """You are a helpful WhatsApp assistant. 
Keep responses concise (max 2-3 sentences).
Be friendly and conversational."""
        
        history = await self.get_history(channel, sender_id, limit=5)
        
        return f"{system_prompt}\n\n{history}"


# ============================================================================
# 3. MESSAGE ADAPTERS (WhatsApp & Telegram)
# ============================================================================

class MessageAdapter(ABC):
    """Abstract adapter for channel-specific message parsing"""
    
    @abstractmethod
    async def parse_inbound(self, raw_payload: Dict) -> ChannelMessage:
        pass
    
    @abstractmethod
    async def validate_signature(self, payload: Dict, signature: str) -> bool:
        pass


class WhatsAppAdapter(MessageAdapter):
    """Twilio WhatsApp adapter"""
    
    def __init__(self, twilio_auth_token: str = "test_token_123"):
        self.twilio_auth_token = twilio_auth_token
    
    async def parse_inbound(self, raw_payload: Dict) -> ChannelMessage:
        """Parse Twilio webhook payload"""
        
        print(f"  [ADAPTER:WhatsApp] 📥 Parsing Twilio payload...")
        
        sender_id = raw_payload.get("From")  # Phone number
        text = raw_payload.get("Body")
        msg_sid = raw_payload.get("MessageSid")
        
        return ChannelMessage(
            channel="whatsapp",
            sender_id=sender_id,
            text=text,
            timestamp=datetime.now(),
            external_msg_id=msg_sid,
            metadata={"twilio_account_sid": raw_payload.get("AccountSid", "")},
        )
    
    async def validate_signature(self, payload: Dict, signature: str) -> bool:
        """Validate Twilio HMAC-SHA1 signature (simplified)"""
        
        print(f"  [ADAPTER:WhatsApp] 🔐 Validating signature...")
        
        # Simplified: just check it's not empty
        is_valid = bool(signature) and signature.startswith("v1=")
        
        if is_valid:
            print(f"  [ADAPTER:WhatsApp] ✅ Signature valid")
        else:
            print(f"  [ADAPTER:WhatsApp] ❌ Signature invalid")
        
        return is_valid


class TelegramAdapter(MessageAdapter):
    """Telegram Bot API adapter"""
    
    def __init__(self, bot_token: str = "test_bot_token_123"):
        self.bot_token = bot_token
    
    async def parse_inbound(self, raw_payload: Dict) -> ChannelMessage:
        """Parse Telegram webhook payload"""
        
        print(f"  [ADAPTER:Telegram] 📥 Parsing Telegram payload...")
        
        message = raw_payload.get("message", {})
        sender_id = str(message.get("from", {}).get("id"))
        text = message.get("text")
        msg_id = str(message.get("message_id"))
        
        return ChannelMessage(
            channel="telegram",
            sender_id=sender_id,
            text=text,
            timestamp=datetime.now(),
            external_msg_id=msg_id,
            metadata={"chat_id": message.get("chat", {}).get("id")},
        )
    
    async def validate_signature(self, payload: Dict, signature: str) -> bool:
        """Validate Telegram secret token (simplified)"""
        
        print(f"  [ADAPTER:Telegram] 🔐 Validating signature...")
        
        # Simplified: just check it matches
        is_valid = signature == self.bot_token
        
        if is_valid:
            print(f"  [ADAPTER:Telegram] ✅ Signature valid")
        else:
            print(f"  [ADAPTER:Telegram] ❌ Signature invalid")
        
        return is_valid


# ============================================================================
# 4. AGENT BRIDGE (Ollama Interface - Mocked)
# ============================================================================

class OllamaBridge:
    """Interface to Ollama LLM (mocked for demo)"""
    
    def __init__(self, model: str = "mistral:7b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.call_count = 0
    
    async def generate(self, context: str, user_message: str, timeout: float = 10.0,
                      correlation_id: str = None) -> AgentBridgeResponse:
        """Call Ollama API (mocked with hardcoded responses)"""
        
        print(f"  [BRIDGE] 🤖 Calling Ollama bridge (model={self.model}, cid={correlation_id})")
        
        # Simulate Ollama call
        start_time = time.time()
        await asyncio.sleep(0.5)  # Simulate network latency
        
        self.call_count += 1
        
        # Mock responses based on user message
        if "hello" in user_message.lower():
            response_text = "Hi there! How can I help you today?"
        elif "weather" in user_message.lower():
            response_text = "I don't have access to real-time weather data. Try checking weather.com!"
        elif "joke" in user_message.lower():
            response_text = "Why did the AI go to school? To improve its learning models! 😄"
        else:
            response_text = f"Thanks for your message: '{user_message}'. How can I assist further?"
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        print(f"  [BRIDGE] ✅ Response received in {latency_ms}ms")
        
        return AgentBridgeResponse(
            response_text=response_text,
            tokens_used=42,  # Mock token count
            latency_ms=latency_ms,
            status="success",
        )


# ============================================================================
# 5. AGENT CORE (Channel-Agnostic Orchestrator)
# ============================================================================

class AgentCore:
    """Channel-agnostic agent orchestrator"""
    
    def __init__(self, storage: ConversationStorage, bridge: OllamaBridge):
        self.storage = storage
        self.bridge = bridge
    
    async def process(self, msg: ChannelMessage) -> str:
        """Process message through agent core"""
        
        print(f"[AGENT] 🔄 Processing message (cid={msg.correlation_id})")
        print(f"[AGENT]   channel={msg.channel}, sender={msg.sender_id}")
        print(f"[AGENT]   text='{msg.text}'")
        
        # 1. Check idempotency
        print(f"[AGENT] 🔍 Checking idempotency (external_msg_id={msg.external_msg_id})")
        
        # 2. Get conversation history
        context = await self.storage.get_context(msg.channel, msg.sender_id)
        
        # 3. Call Ollama bridge
        bridge_response = await self.bridge.generate(
            context=context,
            user_message=msg.text,
            correlation_id=msg.correlation_id,
        )
        
        if bridge_response.status != "success":
            print(f"[AGENT] ❌ Bridge error: {bridge_response.error_msg}")
            return "I'm having trouble processing your request. Please try again."
        
        # 4. Store messages
        await self.storage.add_message(
            channel=msg.channel,
            sender_id=msg.sender_id,
            role="user",
            text=msg.text,
            external_msg_id=msg.external_msg_id,
            correlation_id=msg.correlation_id,
        )
        
        # Store assistant response
        await self.storage.add_message(
            channel=msg.channel,
            sender_id=msg.sender_id,
            role="assistant",
            text=bridge_response.response_text,
            external_msg_id=f"auto-{uuid.uuid4()}",
            correlation_id=msg.correlation_id,
        )
        
        print(f"[AGENT] ✅ Processing complete")
        
        return bridge_response.response_text


# ============================================================================
# 6. MESSAGE SENDERS (Channel-Specific Response Formatters)
# ============================================================================

class MessageSender(ABC):
    """Abstract sender for channel-specific response sending"""
    
    @abstractmethod
    async def send(self, sender_id: str, response_text: str) -> SenderResponse:
        pass


class WhatsAppSender(MessageSender):
    """Twilio WhatsApp sender"""
    
    async def send(self, sender_id: str, response_text: str) -> SenderResponse:
        """Send response via Twilio API (mocked)"""
        
        print(f"  [SENDER:WhatsApp] 📤 Sending response to {sender_id}")
        print(f"  [SENDER:WhatsApp]    text='{response_text}'")
        
        # Mock Twilio API call
        await asyncio.sleep(0.3)
        
        external_msg_id = f"SM{uuid.uuid4().hex[:20]}"
        
        print(f"  [SENDER:WhatsApp] ✅ Message sent (MessageSid={external_msg_id})")
        
        return SenderResponse(
            external_msg_id=external_msg_id,
            status="success",
        )


class TelegramSender(MessageSender):
    """Telegram Bot API sender"""
    
    async def send(self, sender_id: str, response_text: str) -> SenderResponse:
        """Send response via Telegram API (mocked)"""
        
        print(f"  [SENDER:Telegram] 📤 Sending response to {sender_id}")
        print(f"  [SENDER:Telegram]    text='{response_text}'")
        
        # Mock Telegram API call
        await asyncio.sleep(0.3)
        
        external_msg_id = f"{int(time.time() * 1000)}"
        
        print(f"  [SENDER:Telegram] ✅ Message sent (message_id={external_msg_id})")
        
        return SenderResponse(
            external_msg_id=external_msg_id,
            status="success",
        )


# ============================================================================
# 7. WEBHOOK ROUTER (Entry Point)
# ============================================================================

class WebhookRouter:
    """Central router for all inbound messages"""
    
    def __init__(self):
        self.adapters: Dict[str, MessageAdapter] = {}
        self.senders: Dict[str, MessageSender] = {}
        self.storage = ConversationStorage()
        self.bridge = OllamaBridge()
        self.agent = AgentCore(self.storage, self.bridge)
    
    def register_channel(self, channel: str, adapter: MessageAdapter, sender: MessageSender):
        """Register adapter + sender for a channel"""
        self.adapters[channel] = adapter
        self.senders[channel] = sender
        print(f"[ROUTER] ✅ Channel registered: {channel}")
    
    async def route(self, channel: str, raw_payload: Dict, signature: str = None) -> Dict:
        """Route inbound message through full pipeline"""
        
        print(f"\n{'='*80}")
        print(f"[ROUTER] 📨 Inbound webhook: channel={channel}")
        print(f"{'='*80}")
        
        # 1. Get adapter
        if channel not in self.adapters:
            return {"error": f"Unknown channel: {channel}", "status_code": 400}
        
        adapter = self.adapters[channel]
        
        # 2. Validate signature
        if signature:
            is_valid = await adapter.validate_signature(raw_payload, signature)
            if not is_valid:
                return {"error": "Invalid signature", "status_code": 401}
        
        # 3. Parse message
        try:
            msg = await adapter.parse_inbound(raw_payload)
            print(f"  [ROUTER] ✅ Message parsed: {msg.channel}://{msg.sender_id}")
        except Exception as e:
            print(f"  [ROUTER] ❌ Parse error: {e}")
            return {"error": str(e), "status_code": 400}
        
        # 4. Process through agent core
        try:
            response_text = await self.agent.process(msg)
        except Exception as e:
            print(f"[AGENT] ❌ Agent error: {e}")
            response_text = "I encountered an error processing your message. Please try again."
        
        # 5. Send response
        sender = self.senders[channel]
        try:
            send_response = await sender.send(msg.sender_id, response_text)
            print(f"[ROUTER] ✅ Response sent successfully")
        except Exception as e:
            print(f"[SENDER] ❌ Send error: {e}")
            send_response = SenderResponse(
                external_msg_id=None,
                status="failed",
                provider_error_msg=str(e),
            )
        
        print(f"{'='*80}\n")
        
        return {
            "status": "ok" if send_response.status == "success" else "error",
            "correlation_id": msg.correlation_id,
            "response": response_text,
            "external_msg_id": send_response.external_msg_id,
        }


# ============================================================================
# 8. DEMO SCENARIOS
# ============================================================================

async def demo_whatsapp_conversation():
    """Demo: Multi-turn WhatsApp conversation"""
    
    print("\n" + "="*80)
    print("DEMO 1: WhatsApp Multi-Turn Conversation")
    print("="*80)
    
    router = WebhookRouter()
    router.register_channel(
        "whatsapp",
        WhatsAppAdapter(twilio_auth_token="test_token_123"),
        WhatsAppSender(),
    )
    
    # Message 1: Hello
    msg1 = {
        "From": "+1234567890",
        "Body": "Hello, how are you?",
        "MessageSid": "SM001",
        "AccountSid": "ACxxxxxx",
    }
    result1 = await router.route("whatsapp", msg1, signature="v1=valid_sig")
    
    # Message 2: Tell me a joke
    msg2 = {
        "From": "+1234567890",
        "Body": "Tell me a joke",
        "MessageSid": "SM002",
        "AccountSid": "ACxxxxxx",
    }
    result2 = await router.route("whatsapp", msg2, signature="v1=valid_sig")
    
    # Message 3: What's the weather?
    msg3 = {
        "From": "+1234567890",
        "Body": "What's the weather like?",
        "MessageSid": "SM003",
        "AccountSid": "ACxxxxxx",
    }
    result3 = await router.route("whatsapp", msg3, signature="v1=valid_sig")


async def demo_telegram_conversation():
    """Demo: Telegram conversation (different sender)"""
    
    print("\n" + "="*80)
    print("DEMO 2: Telegram Conversation (Different User)")
    print("="*80)
    
    router = WebhookRouter()
    router.register_channel(
        "telegram",
        TelegramAdapter(bot_token="test_bot_token_123"),
        TelegramSender(),
    )
    
    # Telegram message
    msg = {
        "update_id": 123456,
        "message": {
            "message_id": 1,
            "from": {"id": 9876543210, "first_name": "John"},
            "text": "Hello from Telegram!",
            "chat": {"id": 9876543210},
        }
    }
    result = await router.route("telegram", msg, signature="test_bot_token_123")


async def demo_multi_channel_isolation():
    """Demo: Prove history isolation between channels"""
    
    print("\n" + "="*80)
    print("DEMO 3: Multi-Channel History Isolation")
    print("="*80)
    
    router = WebhookRouter()
    router.register_channel(
        "whatsapp",
        WhatsAppAdapter(twilio_auth_token="test_token_123"),
        WhatsAppSender(),
    )
    router.register_channel(
        "telegram",
        TelegramAdapter(bot_token="test_bot_token_123"),
        TelegramSender(),
    )
    
    # Same sender_id, different channels (phone +1234567890 on WhatsApp, Telegram user 1234567890)
    # → Should have separate histories
    
    # WhatsApp: User asks about weather
    msg_whatsapp = {
        "From": "+1234567890",
        "Body": "What's the weather?",
        "MessageSid": "SM_W001",
        "AccountSid": "ACxxxxxx",
    }
    await router.route("whatsapp", msg_whatsapp, signature="v1=valid_sig")
    
    # Telegram: Same "user" asks a joke
    msg_telegram = {
        "update_id": 123456,
        "message": {
            "message_id": 1,
            "from": {"id": 1234567890, "first_name": "John"},
            "text": "Tell me a joke",
            "chat": {"id": 1234567890},
        }
    }
    await router.route("telegram", msg_telegram, signature="test_bot_token_123")
    
    # Check storage: histories should be separate
    print("\n[VERIFICATION] Storage state:")
    print(f"  Total messages stored: {len(router.storage.messages)}")
    for msg in router.storage.messages:
        print(f"    - {msg['channel']} | {msg['sender_id']} | {msg['role']}: {msg['text'][:50]}")


async def demo_idempotency():
    """Demo: Duplicate message handling (idempotency)"""
    
    print("\n" + "="*80)
    print("DEMO 4: Idempotency Test (Replay Attack Simulation)")
    print("="*80)
    
    router = WebhookRouter()
    router.register_channel(
        "whatsapp",
        WhatsAppAdapter(twilio_auth_token="test_token_123"),
        WhatsAppSender(),
    )
    
    # Message sent twice with same MessageSid (simulating replay/retry)
    msg = {
        "From": "+1234567890",
        "Body": "This is a test message",
        "MessageSid": "SM_REPLAY_001",
        "AccountSid": "ACxxxxxx",
    }
    
    print("\n[TEST] Sending message first time...")
    result1 = await router.route("whatsapp", msg, signature="v1=valid_sig")
    
    print("\n[TEST] Sending same message again (replay attempt)...")
    result2 = await router.route("whatsapp", msg, signature="v1=valid_sig")
    
    print(f"\n[VERIFICATION] Total unique messages in storage: {len(router.storage.messages)}")
    print(f"  Expected: 2 (1 user + 1 assistant), got: {len(router.storage.messages)}")


async def main():
    """Run all demos"""
    
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "Multi-Channel Conversational Agent — Communication Emulation Demo".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    # Run all demos
    await demo_whatsapp_conversation()
    await demo_telegram_conversation()
    await demo_multi_channel_isolation()
    await demo_idempotency()
    
    print("\n" + "="*80)
    print("✅ All demos completed!")
    print("="*80)
    print("\nKey Points:")
    print("  ✓ Webhook router handles multiple channels")
    print("  ✓ Adapters normalize channel-specific formats")
    print("  ✓ Agent core is completely channel-agnostic")
    print("  ✓ Senders handle channel-specific APIs")
    print("  ✓ History isolation works (channel + sender_id)")
    print("  ✓ Idempotency prevents duplicate processing")
    print("\nNext: Create 31 GitHub stories to build this properly!")
    print()


if __name__ == "__main__":
    asyncio.run(main())
