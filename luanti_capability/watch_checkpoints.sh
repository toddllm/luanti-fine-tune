#!/usr/bin/env bash
watch -n 15 'ls -lh outputs_*/checkpoint-* 2>/dev/null | tail -n 5'
