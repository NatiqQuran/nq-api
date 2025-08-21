import * as AuthType from "../types/auth";
import { AxiosResponse } from "axios";
import { Connection } from "../client/connection";
import { BaseController } from "../utils/baseController";
import { RequestConfig } from "../utils/globalTypes";

export class AuthLogin extends BaseController {
    constructor(conn: Connection, token?: string) {
        super(conn, token);
    }
    /** POST /auth/login/ */
    async auth_login_create(data: AuthType.AuthLoginRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<AuthType.AuthLoginResponseData>> {
        return await this.axiosPost(`/auth/login/`, data, config);
    }
}

export class AuthLogout extends BaseController {
    constructor(conn: Connection, token?: string) {
        super(conn, token);
    }
    /** POST /auth/logout/ */
    async auth_logout_create(config?: RequestConfig
    ): Promise<AxiosResponse<any>> {
        return await this.axiosPost(`/auth/logout/`, config);
    }
}

export class AuthLogoutall extends BaseController {
    constructor(conn: Connection, token?: string) {
        super(conn, token);
    }
    /** POST /auth/logoutall/ */
    async auth_logoutall_create(config?: RequestConfig
    ): Promise<AxiosResponse<any>> {
        return await this.axiosPost(`/auth/logoutall/`, config);
    }
}

export class AuthRegister extends BaseController {
    constructor(conn: Connection, token?: string) {
        super(conn, token);
    }
    /** POST /auth/register/ */
    async auth_register_create(data: AuthType.AuthRegisterRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<AuthType.AuthRegisterResponseData>> {
        return await this.axiosPost(`/auth/register/`, data, config);
    }
}

export class AuthController extends BaseController {
    public readonly login: AuthLogin;
    public readonly logout: AuthLogout;
    public readonly logoutall: AuthLogoutall;
    public readonly register: AuthRegister;

    constructor(connection: Connection, token?: string) {
        super(connection, token);
        this.login = new AuthLogin(this.conn);
        this.logout = new AuthLogout(this.conn);
        this.logoutall = new AuthLogoutall(this.conn);
        this.register = new AuthRegister(this.conn);
    }
    
}