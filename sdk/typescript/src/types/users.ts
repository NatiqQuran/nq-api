
export type UsersListResponseData = User[];
export interface UsersCreateRequestData {
    email: string;
    first_name?: string;
    last_name?: string;
    password: string;
    password2: string;
    username: string;
}
export interface UsersCreateResponseData {
    email: string;
    first_name?: string;
    last_name?: string;
    password: string;
    password2: string;
    username: string;
}
export interface UsersRetrieveResponseData {
    email: string;
    first_name?: string;
    last_name?: string;
    password: string;
    password2: string;
    username: string;
}
export interface UsersUpdateRequestData {
    email: string;
    first_name?: string;
    last_name?: string;
    password: string;
    password2: string;
    username: string;
}
export interface UsersUpdateResponseData {
    email: string;
    first_name?: string;
    last_name?: string;
    password: string;
    password2: string;
    username: string;
}
export interface UsersPartialupdateRequestData {
    email?: string;
    first_name?: string;
    last_name?: string;
    password?: string;
    password2?: string;
    username?: string;
}
export interface UsersPartialupdateResponseData {
    email: string;
    first_name?: string;
    last_name?: string;
    password: string;
    password2: string;
    username: string;
}


export interface User {
    uuid: string;
    username: string;
    email: string;
    first_name?: string;
    last_name?: string;
    password: string;
    password2: string;
}