from __future__ import annotations

import sys
from logging import Logger
from pathlib import Path
from typing import Optional, Union

from loguru import logger as _logger

PathLike = Union[str, Path]


def create_logger(
    log_dir: Optional[PathLike] = "logs",
    level: str = "INFO",
    dev_mode: bool = False,
    rotation: str = "10 MB",
    retention: str = "14 days",
    compression: str = "zip",
    enqueue: bool = True,
    diagnose: bool = False,
) -> Logger:
    """configure and return a production-grade loguru logger.
    provides structured logging, rotation, multiprocessing safety, and clean console output suitable for pipelines.

    Args:
        log_dir (Optional[PathLike], optional): directory where logs are stored. Defaults to "logs".
        level (str, optional): base log level. Only applies to stdout. Defaults to "INFO".
        dev_mode (bool, optional): enable trace/debug in console. Defaults to False.
        rotation (str, optional): file rotation policy. Defaults to "10 MB".
        retention (str, optional): log retention policy. Defaults to "14 days".
        compression (str, optional): compression for rotated logs. Defaults to "zip".
        enqueue (bool, optional): queue logs for multiprocessing safety. Defaults to True.
        diagnose (bool, optional): include variable values in tracebacks. Defaults to False.

    Returns:
        logger: configured logger proxy
    """
    _logger.remove()

    # level styling for console readability
    level_styles = {
        "TRACE": {"color": "<white><dim>"},
        "DEBUG": {"color": "<white>"},
        "INFO": {"color": "<blue>"},
        "SUCCESS": {"color": "<green><bold>"},
        "WARNING": {"color": "<yellow>"},
        "ERROR": {"color": "<red><bold>"},
        "CRITICAL": {"color": "<bg red><fg black><bold>"},
    }
    for name, style in level_styles.items():
        _logger.level(name, **style)

    # console log format
    console_fmt = (
        "<white><dim>{time:%I:%M %p %z}</dim></white> | "
        "<white><dim>{module:<10}</dim></white> | "
        "<level>{level:<9}</level> | <level>{message}</level>"
    )
    # file log format
    file_fmt = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS Z} | {level:<9} | {module:<12} | {message}"
    )

    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)

    # stdout: operational output
    # in case dev mode is enabled
    # also log debug and trace
    stdout_levels = {"INFO", "SUCCESS"}
    if dev_mode:
        stdout_levels |= {"DEBUG", "TRACE"}
    _logger.add(
        sys.stdout,
        filter=lambda r: r["level"].name in stdout_levels,
        format=console_fmt,
        level=level,
        colorize=True,
        enqueue=enqueue,
        backtrace=False,
        diagnose=diagnose,
    )
    # stderr: problems & diagnostics
    _logger.add(
        sys.stderr,
        level="WARNING",
        format=console_fmt,
        colorize=True,
        enqueue=enqueue,
        backtrace=True,
        diagnose=diagnose,
    )

    if log_dir:
        # warning+ structured logs (alerts, monitoring)
        _logger.add(
            Path(log_dir) / "warning_plus.jsonl",
            level="WARNING",
            serialize=True,
            rotation=rotation,
            retention=retention,
            compression=compression,
            enqueue=enqueue,
        )

        # info+ structured logs (analytics & ops)
        _logger.add(
            Path(log_dir) / "info_plus.jsonl",
            level="INFO",
            serialize=True,
            rotation=rotation,
            retention=retention,
            compression=compression,
            enqueue=enqueue,
        )

        # trace/debug developer logs
        _logger.add(
            Path(log_dir) / "trace_debug.log",
            level="TRACE",
            filter=lambda r: r["level"].name in {"TRACE", "DEBUG"},
            format=file_fmt,
            rotation=rotation,
            retention=retention,
            compression=compression,
            enqueue=enqueue,
        )

        # full audit trail
        _logger.add(
            Path(log_dir) / "all.log",
            level="TRACE",
            format=file_fmt,
            rotation=rotation,
            retention=retention,
            compression=compression,
            enqueue=enqueue,
        )

    # ensure caller module is reported correctly
    class LoggerProxy:
        def __init__(self, base):
            self._base = base

        def __getattr__(self, name):
            return getattr(self._base.opt(depth=1), name)

    return LoggerProxy(_logger)
