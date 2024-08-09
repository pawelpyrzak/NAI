package com.example.multimodule.Exceptions;

public class MessagesNotFoundException extends RuntimeException {
    public MessagesNotFoundException(String message) {
        super(message);
    }
}

