package com.example.multimodule.Exceptions;

public class InvitationExpiredException extends RuntimeException {
    public InvitationExpiredException(String message) {
        super(message);
    }
}
