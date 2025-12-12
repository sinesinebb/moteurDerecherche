# src/processors/async_kafka_consumer.py
"""
Async wrapper around aiokafka.AIOKafkaConsumer.

Usage:
    consumer = AIOConsumer(config_dict, ["topic1"], loop)
    task = loop.create_task(consumer.consume(handler))
"""
import asyncio
import logging
from typing import Any, Callable, Dict, Iterable, Optional

logger = logging.getLogger("indexing-service.async_kafka_consumer")

try:
    from aiokafka import AIOKafkaConsumer
    AIOMQ = True
except Exception:  # pragma: no cover - fallback if aiokafka not available
    AIOKafkaConsumer = None  # type: ignore
    AIOMQ = False
    logger.warning("aiokafka not available, AIOConsumer will simulate consumption.")


class AIOConsumer:
    """
    Lightweight async wrapper for aiokafka consumer.

    The constructor accepts a config dict similar to confluent style (bootstrap.servers, group.id, ...).
    """

    def __init__(self, config: Dict[str, Any], topics: Iterable[str], loop: Optional[asyncio.AbstractEventLoop] = None):
        self._loop = loop or asyncio.get_event_loop()
        self._topics = list(topics)
        self._raw_config = dict(config or {})
        self._consumer: Optional[AIOKafkaConsumer] = None
        self._running = False

        if AIOMQ:
            kafka_kwargs: Dict[str, Any] = {}

            # translation from common confluent keys
            if "bootstrap.servers" in self._raw_config:
                kafka_kwargs["bootstrap_servers"] = self._raw_config["bootstrap.servers"]
            elif "bootstrap_servers" in self._raw_config:
                kafka_kwargs["bootstrap_servers"] = self._raw_config["bootstrap_servers"]

            if "group.id" in self._raw_config:
                kafka_kwargs["group_id"] = self._raw_config["group.id"]
            elif "group_id" in self._raw_config:
                kafka_kwargs["group_id"] = self._raw_config["group_id"]

            kafka_kwargs["auto_offset_reset"] = self._raw_config.get("auto.offset.reset", "earliest")

            # map enable.auto.commit if present
            if "enable.auto.commit" in self._raw_config:
                kafka_kwargs["enable_auto_commit"] = self._raw_config["enable.auto.commit"]

            # allow passing additional aiokafka kwargs directly
            for k, v in self._raw_config.items():
                if k in ("bootstrap_servers", "group_id", "auto_offset_reset", "enable_auto_commit"):
                    continue
                # accept aiokafka-style keys if provided
                if k in ("security_protocol", "sasl_mechanism", "sasl_plain_username", "sasl_plain_password"):
                    kafka_kwargs[k] = v

            # instantiate the aiokafka consumer
            self._consumer = AIOKafkaConsumer(*self._topics, loop=self._loop, **kafka_kwargs)
            logger.debug("AIOConsumer created (aiokafka present). kwargs=%s topics=%s", kafka_kwargs, self._topics)
        else:
            logger.info("aiokafka not installed: AIOConsumer will simulate consumption (no real messages).")

    async def start(self) -> None:
        """Start underlying aiokafka consumer if available."""
        if not AIOMQ:
            logger.debug("start() called but aiokafka not installed - nothing to start.")
            return
        if self._consumer is None:
            raise RuntimeError("Consumer not initialized")
        if not self._running:
            await self._consumer.start()
            self._running = True
            logger.info("AIOConsumer started and subscribed to %s", self._topics)

    async def stop(self) -> None:
        """Stop underlying aiokafka consumer if available."""
        if not AIOMQ:
            logger.debug("stop() called but aiokafka not installed - nothing to stop.")
            return
        if self._consumer is not None and self._running:
            try:
                await self._consumer.stop()
            finally:
                self._running = False
            logger.info("AIOConsumer stopped")

    async def consume(self, handler: Callable[[Any], Any]) -> None:
        """
        Main consumption loop. `handler` may be sync or async and is invoked for each message.

        The message argument is the aiokafka ConsumerRecord.
        """
        if not AIOMQ:
            # simulated long-running no-op (keeps app alive)
            logger.warning("consume() called but aiokafka not installed — simulating no-op (sleep loop).")
            while True:
                await asyncio.sleep(3600)

        assert self._consumer is not None, "aiokafka consumer not initialized"
        await self.start()

        try:
            async for msg in self._consumer:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(msg)
                    else:
                        # run synchronous handler in executor to avoid blocking the loop
                        await self._loop.run_in_executor(None, handler, msg)
                except Exception:
                    logger.exception("Error while handling message (continuing to next message)")
        except asyncio.CancelledError:
            logger.debug("consume loop cancelled (received CancelledError)")
            raise
        except Exception:
            logger.exception("Unhandled exception in consume loop (will stop)")
            raise
        finally:
            try:
                await self.stop()
            except Exception:
                logger.exception("Error while stopping consumer in finally block")
