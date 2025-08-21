import * as UsersType from "../types/users";
import { AxiosResponse } from "axios";
import { Connection } from "../client/connection";
import { BaseController } from "../utils/baseController";
import { RequestConfig } from "../utils/globalTypes";

export class UsersController extends BaseController {

    constructor(connection: Connection, token?: string) {
        super(connection, token);
    }
    
    /** GET /users/ */
    async list(config?: RequestConfig
    ): Promise<AxiosResponse<UsersType.UsersListResponseData>> {
        return await this.axiosGet(`/users/`, config);
    }
    
    /** POST /users/ */
    async create(data: UsersType.UsersCreateRequestData,config?: RequestConfig
    ): Promise<AxiosResponse<UsersType.UsersCreateResponseData>> {
        return await this.axiosPost(`/users/`, data, config);
    }
    
    /** GET /users/{uuid}/ */
    async retrieve(uuid: string,config?: RequestConfig
    ): Promise<AxiosResponse<UsersType.UsersRetrieveResponseData>> {
        return await this.axiosGet(`/users/${uuid}/`, config);
    }
    
    /** PUT /users/{uuid}/ */
    async update(uuid: string,data: UsersType.UsersUpdateRequestData,config?: RequestConfig
    ): Promise<AxiosResponse<UsersType.UsersUpdateResponseData>> {
        return await this.axiosPut(`/users/${uuid}/`, data, config);
    }
    
    /** PATCH /users/{uuid}/ */
    async partialUpdate(uuid: string,data: UsersType.UsersPartialupdateRequestData,config?: RequestConfig
    ): Promise<AxiosResponse<UsersType.UsersPartialupdateResponseData>> {
        return await this.axiosPatch(`/users/${uuid}/`, data, config);
    }
    
    /** DELETE /users/{uuid}/ */
    async delete(uuid: string,config?: RequestConfig
    ): Promise<AxiosResponse<any>> {
        return await this.axiosDelete(`/users/${uuid}/`, config);
    }
    
}