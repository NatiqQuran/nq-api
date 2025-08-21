
export interface AuthLoginRequestData {
    password: string;
    username: string;
}
export interface AuthLoginResponseData {
    expiry: string;
    token: string;
    user: object;
}
export interface AuthRegisterRequestData {
    email: string;
    first_name?: string;
    last_name?: string;
    password: string;
    password2: string;
    username: string;
}
export interface AuthRegisterResponseData {
    token: string;
    user: object;
}

