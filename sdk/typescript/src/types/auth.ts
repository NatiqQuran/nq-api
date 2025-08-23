
export interface AuthLoginPostRequestData {
    password: string;
    username: string;
}
export interface AuthLoginPostResponseData {
    expiry: string;
    token: string;
    user: object;
}
export interface AuthRegisterPostRequestData {
    email: string;
    first_name?: string;
    last_name?: string;
    password: string;
    password2: string;
    username: string;
}
export interface AuthRegisterPostResponseData {
    token: string;
    user: object;
}

